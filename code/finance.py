'''

'''
import pandas as pd
import numpy as np

COLUMNS_KEY = {'A1': 'Classroom Salaries',
               'A2': 'Other Instructional Salaries',
               'A3': 'Instructional Benefits',
               'A4': 'Professional Development',
               'A': 'Instructional Spending',
               'B1': 'School Administrative Salaries',
               'B2': 'School Administrative Benefits',
               'B3': 'Other School Administrative Expenditures',
               'B': 'Administration Spending',
               'C1': 'All Other Salaries',
               'C2': 'All Other Benefits',
               'C3': 'All Other Non-personnel Expenditures',
               'C': 'Other Spending',
               'D': 'Total School Level Spending',
               'J': 'Local/State Spending',
               'K1': 'Federal Title I Part A',
               'K2': 'Federal Title II Part A',
               'K3': 'Federal Title III Part A',
               'K4': 'Federal Title IV Part A',
               'K5': 'IDEA',
               'K6': 'All Other Federal',
               'K': 'Total Federal Spending',
               'O': 'Special Education',
               'P': 'ELL/MLL Services',
               'Q': 'Pupil Services',
               'R': 'Community Schools Programs',
               'T': 'Prekindergarten'}

ABBREVIATIONS_MAP = dict([('high school', 'hs'),
                         ('secondary school', 'hs'),
                         ('secondary sch', 'hs'),
                         ('secondary', 'hs'),
                         ('secondar', 'hs'),
                         ('elementary school', 'elem'),
                         ('elementary', 'elem'),
                         ('middle school', 'ms'),
                         ('public school', 'ps'),
                         ('junior high school', 'jhs'),
                         ('academy', 'acad'),
                         ('preparatory', 'prep'),
                         ('school', 'sch'),
                         ('american', 'amer'),
                         ('language', 'lang'),
                         ('english', 'engl'),
                         ('mathematics', 'math'),
                         ('technology','tech'),
                         ('technical','tech'),
                         ('education', 'ed'),
                         ('sciences', 'sci'),
                         ('science', 'sci'),
                         ('scien', 'sci'),
                         ('engineering', 'eng'),
                         ('engineeri', 'eng'),
                         ('engnrng', 'eng'),
                         ('advocacy', 'advcy'),
                         ('community', 'comm'),
                         ('justic', 'just'),
                         ('business', 'bus'),
                         ('careers', 'car'),
                         ('career', 'car'),
                         ('television', 'tv'),
                         ('craftsmanship', 'craft'),
                         ('craftsman', 'craft'),
                         ('new york city', 'nyc'),
                         ('building', 'bldg'),
                         ('performing', 'perf'),
                         ('perform', 'perf'),
                         ('visual', 'vis'),
                         ('young', 'yng'),
                         ('-', ' '),
                         (' for ', ' '),
                         (' of ', ' '),
                         ('and', ' '),
                         ('&', ' '),
                         ('   ', ' '),
                         ('  ', ' ')])

TOTAL = ['D']
GRP_TOTALS = ['A', 'B', 'C']
SUBGROUPS = ['A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'C1', 'C2', 'C3']
FED_VS_LOCAL = ['J', 'K']
FED_VS_LOCAL_SUB = ['J', 'K1', 'K2', 'K3', 'K4', 'K5', 'K6']
OTHER = ['O', 'P', 'Q', 'R', 'T']
ALL = [*GRP_TOTALS, *SUBGROUPS, 'D', *FED_VS_LOCAL_SUB, 'K']

def _rename_finance(col_name):
    if col_name == 'District':
        col_name = 'district'
    elif col_name == 'School':
        col_name = 'school'
    elif 'GROUP' in col_name:
        col_name = col_name.split()[1]
    else:
        col_name = col_name.split('.')[0]
    return col_name

def _clean_cash(val):
    if isinstance(val, str) and val[0] == '$':
        val = float(''.join(val.split(',')).strip('$'))
    return val

def _school_name_format(string):
    string = string.lower()
    if '(the)' in string:
        string = string.replace('(the)', '').strip()
    elif '(the' in string:
        string = string.replace('(the', '').strip()
    elif (('the ' in string[:5]) or (' the ' in string) or \
            (' the' in string[-5:])):
        string = string.replace('the', '').strip()

    for (k, v) in ABBREVIATIONS_MAP.items():
        if k in string:
            string = string.replace(k, v)
    return string

def _clean(df):
    # df = df.reset_index(drop=False)
    df = df.rename(columns=lambda col: _rename_finance(col))
    df['school'] = df['school'].map(lambda x: _school_name_format(x))
    df = df.set_index('school')
    df = df.applymap(lambda x: _clean_cash(x))
    del [df['B3'], df['I'], df['N'], df['S']]
    # df = df.astype(float)
    return df

def name_of_file(num):
    dist = ''
    if num < 7:
        dist = 'MANHATTAN'
        num = f' {num}'
    elif num < 13:
        dist = 'BRONX'
        if num < 10:
            num = f' {num}'
    elif (num < 24) or (num == 32):
        dist = 'BROOKLYN'
    elif num < 31:
        dist = 'QUEENS'
    elif num == 31:
        dist = 'STATEN ISLAND'

    file_name = f'NYC GEOG DIST #{num} - {dist}'
    file_path = f'./data/finance_data/{file_name}.csv'
    return file_path

def create_frame(*args):
    try:
        if len(args) == 0:
            nums = list(range(1,32))
        elif len(args) == 1:
            nums = list(range(1, args[0]+1))
        elif len(args) == 2:
            nums = list(range(args[0],args[1]+1))
        else:
            raise ValueError('Too many arguments')
    except:
        raise ValueError('Arguments must be integers')
    df = pd.DataFrame()
    for num in nums:
        df = df.append(pd.read_csv(name_of_file(num)))
    df = _clean(df)
    return df
