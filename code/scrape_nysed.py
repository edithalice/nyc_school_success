'''
'''
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import os
import sys
import re


def new_window(driver, prev_windows):
    '''
    Switch to the open window not in args.
    '''
    for window_handle in driver.window_handles:
        if window_handle not in prev_windows:
            driver.switch_to.window(window_handle)
            break
    return

def find_districts(driver):
    '''
    Return a list of elements containing each school district in NYC on page.
    '''
    nyc_districts = []
    for row in range(14,25):
        for col in range(1,4):
            if (row == 24 and col == 3): break
            nyc_districts.append(driver.find_element_by_xpath(f'/html/body\
                                /section/div[{row}]/div[{col}]/div[1]/a'))
    return nyc_districts

def find_schools(driver, district, windows):
    '''
    Return the district name for input element, along with the elements
    corresponding to each school on the district page.

    Arguments:
    district - web element corresponding to a district on the main page
    windows - a list containg the window handle of the main page
    '''
    district_name = district.text.strip()
    new_url = district.get_property('href')
    driver.execute_script('''window.open("", "_blank");''')
    new_window(driver, windows)
    driver.get(new_url)
    section = driver.find_element_by_class_name('institution-list')
    schools = section.find_elements_by_class_name('bullet-item')
    school_links = []
    for school in schools:
        school_links.append(school.find_element_by_tag_name('a'))
    return (district_name, school_links)

def get_school_data(driver, school, district_name, windows):
    '''
    Return a dictionary containing the financial data from school of args

    Arguments:
    school - web element corresponding to a school on the district page
    district_name - string containing the district name
    windows - list of window handles for the main and district pages
    '''
    school_name = school.text.strip()
    new_url = school.get_property('href')
    driver.execute_script('''window.open("", "_blank");''')
    new_window(driver, windows)
    driver.get(new_url)
    try:
        next_page = driver.find_element_by_link_text('Financial Transparency Report')
        driver.get(next_page.get_property('href'))
    except:
        driver.close()
        driver.switch_to.window(windows[1])
        return None
    soup = BeautifulSoup(driver.page_source, features='lxml')
    dict_1 = {'District':district_name}
    for data in soup.find_all(attrs={'data-label':re.compile(rf'{re.escape(school_name)}')}):
        if data.string and data.parent.get('class') != ['expand']:
            if data.parent.th:
                dict_1[data.parent.th.string] = data.string
            else:
                dict_1[data.parent.td.string] = data.string
    driver.close()
    driver.switch_to.window(windows[1])
    # if dict_1 == {'District':district_name}:
    #     return None
    # else:
    return (school_name, dict_1)

def combine_schools(driver, district):
    '''
    Return a list of school names and a corresponding list of financial data

    Arguments:
    district - web element corresponding to a districton main page
    '''
    school_names = []
    school_data = []
    windows = [driver.current_window_handle]
    district_name, schools = find_schools(driver, district, windows)
    windows.append(driver.current_window_handle)
    for school in schools:
        school_info = get_school_data(driver, school, district_name, windows)
        if school_info:
            school_data.append(school_info[1])
            school_names.append(school_info[0])
    del windows[1]
    driver.close()
    driver.switch_to.window(windows[0])
    df = pd.DataFrame(school_data)
    df = df.rename({i:n for i, n in enumerate(school_names)})
    df.to_csv(path_or_buf=f'./finance_data/{district_name}.csv')
    school_names.clear()
    school_data.clear()
    return #(school_names, school_data)

def scrape_districts(start_index, end_index=32):
    '''
    Return a list of school names and a corresponding list of financial data

    Arguments:
    start_index - district to begin with (in case some some districts have already been scraped)
    end_index - district to stop with
    '''
    for i in range(start_index, end_index):
        driver = webdriver.Safari(keep_alive=True)
        driver.get('https://data.nysed.gov/lists.php?start=78&type=district')
        row = 14 + (i//3)
        col = (i%3) + 1
        district = driver.find_element_by_xpath(f'/html/body/section/div[{row}]/div[{col}]/div[1]/a')
        combine_schools(driver, district)
        driver.quit()
    return

def replace_missing(num):
    '''
    Replace rows of missing data with the correct data.

    Some of the data referred to the school names with a trailing whitespace. I only caught and fixed this halfway through scraping the data, so some of the csvs had empty rows for those schools. Rather than re scrape all the data, or enter the data manually, I wrote this function to find and replace the missing values.
    Argument:
    num - district number to check
    '''
    import finance as fin
    file_path = fin.name_of_file(num)
    df = pd.read_csv(file_path, index_col=0, memory_map=True)
    missing = list(df[df['GROUP A TOTAL'].isna()].index)

    driver = webdriver.Safari(keep_alive=True)
    driver.get('https://data.nysed.gov/lists.php?start=78&type=district')
    i = num - 1
    row = 14 + (i//3)
    col = (i%3) + 1
    district = driver.find_element_by_xpath(f'/html/body/section/div[{row}]/div[{col}]/div[1]/a')

    windows = [driver.current_window_handle]
    district_name, schools = find_schools(driver, district, windows)
    windows.append(driver.current_window_handle)
    for school in schools:
        if school.text.strip() in missing:
            index, data = get_school_data(driver, school, district_name, windows)
            df.loc[index] = data

    driver.quit()
    df.to_csv(path_or_buf=file_path)
    return


def main(argv):
    if not os.path.isdir('./data/finance_data'):
        os.mkdir('./data/finance_data')
    start_index = 0 if len(argv) == 0 else int(argv[0])
    end_index = 32 if len(argv) < 2 else int(argv[1])
    scrape_districts(start_index, end_index)
    return

if __name__ == '__main__':
    main(sys.argv[1:])
