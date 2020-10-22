'''


Possible function calls:
- summary_table()
- summary_numerical()
- success_table()
- target()
- all()
'''
import pandas as pd
import numpy as np

COLUMNS = {'Enrollment':'enroll',
           'School Type':'type',
           'School Name':'school',
           'Rigorous Instruction - Percent Positive':'instr_rat',
           'Collaborative Teachers - Percent Positive':'tchrs_rat',
           'Supportive Environment - Percent Positive':'env_rat',
           'Effective School Leadership - Percent Positive':'ldr_rat',
           'Strong Family-Community Ties - Percent Positive': 'comm_rat',
           'Trust - Percent Positive':'trust_rat',
           'Average Incoming ELA Proficiency (Based on 5th Grade)':\
           'grd_5_english',
           'Average Incoming Math Proficiency (Based on 5th Grade)':\
           'grd_5_math',
           'Percent English Language Learners':'ell',
           'Percent Students with Disabilities':'iep',
           'Percent Self-Contained':'slf_cont',
           'Economic Need Index':'econ_need',
           'Percent in Temp Housing':'temp_hous',
           'Percent HRA Eligible':'hra',
           'Percent Asian':'asian',
           'Percent Black':'black',
           'Percent Hispanic':'hisp',
           'Percent White':'white',
           'Years of principal experience at this school':'prncpl_exp',
           'Percent of teachers with 3 or more years of experience': \
                'tchrs_w_exp',
           'Student Attendance Rate':'attend',
           'Percent of Students Chronically Absent':'chron_abs',
           'Teacher Attendance Rate':'tchr_attend',
           'Average Grade 8 English Proficiency':'grd_8_english',
           'Average Grade 8 Math Proficiency':'grd_8_math',
           'Percent Overage/Undercredited':'overage',
           'Student Achievement - Section Score':'achievement'}

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

SUBJ_RATINGS = ['instr_rat','tchrs_rat','env_rat','ldr_rat','comm_rat',\
                'trust_rat']
RACE = ['asian','black','hisp','white','ell']
DISABIL = ['iep','slf_cont']
INCOMING_PROF = ['incm_eng', 'incm_math']
ECONOMIC = ['econ_need','temp_hous','hra']
ATTENDANCE = ['attend','chron_abs','overage']
STAFF = ['prncpl_exp','tchrs_w_exp','tchr_attend']
ALL = ['enroll', *RACE, *DISABIL, *ECONOMIC, *ATTENDANCE, *STAFF, *SUBJ_RATINGS]

def _simple_school_type(string):
    if string == 'High School':
        string = 'hs'
    elif string == 'Elementary':
        string = 'elem'
    elif string == 'Middle':
        string = 'ms'
    elif string == 'K-8':
        string = 'elem, ms'
    else:
        string = 'Other'
    return string

def _percent_to_dec(val):
    if isinstance(val, str):
        if '%' in val:
            val = float(val.strip('%'))/100
    return val

def _school_name_format(string):
    string = ''.join(str.lower(string).split('.'))
    string = ''.join(str.lower(string).split(','))
    if (('the ' in string[:5]) or (' the ' in string) or \
            (' the' in string[-5:])):
        string = string.replace('the', '').strip()
    for (k, v) in ABBREVIATIONS_MAP.items():
        if k in string:
            string = string.replace(k, v)
    return string

def _merge_prof(df):
    df_prof = df[['grd_5_english', 'grd_5_math','grd_8_english', 'grd_8_math']]\
            .fillna(0)
    df['incm_eng'] = df_prof['grd_5_english'].add(df_prof['grd_8_english'])
    df['incm_math'] = df_prof['grd_5_math'].add(df_prof['grd_8_math'])
    df['incm_eng'] = df['incm_eng'].replace(to_replace=0,value=np.nan)
    df['incm_math'] = df['incm_math'].replace(to_replace=0,value=np.nan)
    df = df.drop(columns=['grd_5_english', 'grd_5_math', 'grd_8_english', 'grd_8_math'])
    return df

def _clean(df):
    df = df.loc[:,~df.columns.duplicated()]
    df = df.replace(to_replace='.',value=np.nan)
    df = df.applymap(lambda x: _percent_to_dec(x))
    df = df.rename(columns=COLUMNS)
    df['type'] = df['type'].map(lambda x: _simple_school_type(x))
    df['school'] = df['school'].map(lambda x: _school_name_format(x))
    df = df.set_index(['school','type'])
    return df

def summary_table():
    ems_sum = pd.read_csv('./data/ems_success/Summary.csv')
    hs_sum = pd.read_csv('./data/hs_success/Summary.csv')

    hs_sum = _clean(hs_sum)
    ems_sum = _clean(ems_sum)

    summary = ems_sum.append(hs_sum)
    summary['overage'] = summary.overage.fillna(0)
    return summary

def summary_numerical():
    df = summary_table()
    cols = [*list(df.columns[1:2]),*list(df.columns[9:15]),\
            *list(df.columns[26:])]
    summary_numer = df[cols].astype(float)
    summary_numer = _merge_prof(summary_numer)
    return summary_numer

def success_table():
    ems_success = pd.read_csv('./data/ems_success/Student Achievement.csv')
    hs_success = pd.read_csv('./data/hs_success/Student Achievement.csv')

    ems_success = _clean(ems_success)
    hs_success = _clean(hs_success)

    success = ems_success.append(hs_success)
    return success

def target():
    df = success_table()
    target_col = df['achievement'].astype(float)
    return target_col

def all():
    df = summary_numerical()
    combined = df.join(target())
    combined = combined.reset_index(level='type')
    return combined
