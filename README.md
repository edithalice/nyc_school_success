# Metis Project 2: NYC School Success
### By Edith Johnston

## Table of Contents
1. [Objective](#objective)
2. [Data Sources](#data-sources)
3. [Modeling Process](#modeling-process)
4. [Main Tools Used](#main-tools-used)
5. [Deliverables](#deliverables)

## Objective:
The purpose of this project was to attempt to build a model that predicts  academic success of NYC public schools, based on available demographic information, as well as funding and spending reports. The point of building this model, however, was not to actually predict success, but rather  to attempt to determine the most influential factors in a school's success (or lack thereof), for the eventual  purpose of mitigating or improving such factors.

## Data Sources:
### Quantifying Success:
The first challenge with this project was how to accurately quantify school success without just resorting to test scores (since test scores are not accurate indicators of future success). For this purpose, I used data from the NYC Department of Education's annual Quality Review. In this survey and review, they evaluate schools by dozens of success metrics, such as adjusted pass rates and subject based proficiency levels. However, they also provide a single aggregate 'Student Achievement Score', which I used as the target variable for my model.
- Source: [NYCED Quality Review](https://infohub.nyced.org/reports/school-quality/school-quality-reports-and-resources)
### School Characteristics
The Quality Review data also included a variety of other information about schools, such as school's racial makeup, demographic information, and a number of qualitative survey response categories (e.g. Supportive Environment, Strong Family Community Ties, etc). However, I also wanted to include information of schools' funding and spending categories, in order to, for one, see if the total amount of funding/or spending impacted success (e.g. better funded schools = more or less successful?), two, see if the category of spending impacted success (e.g. spending more on teacher salaries, classroom material, teacher training, etc = more or less successful?), and three, see if the source of school funding impacted success (e.g. more local funding vs federal funding = more or less successful). The New York State Education Department has this categorized information available of their data site, but the only downloadable files of this data that I found were in a format that required paid software to read, so instead, I wrote a script to navigate the web pages and parse the necessary data from the html pages.
- Source: [NYSED Data site district pages](https://data.nysed.gov/lists.php?start=78&type=district) (I pulled data from the Funding Transparency Reports for each school in each NYC district.)
### Code
- Notebook: [Data Acquisition Process](https://github.com/edithalice/nyc_school_success/blob/master/1.%20Data%20Collection%20and%20Cleaning.ipynb)
- Python Script: [Web Scraping](https://github.com/edithalice/nyc_school_success/blob/master/scrape_nysed.py) - designed to be run from the command line, but explained in the above notebook  
#### Python Modules (utilized and explained in above notebook)
- [Data Cleaning (Quality Review)](https://github.com/edithalice/nyc_school_success/blob/master/success.py)
- [Data Cleaning (NYSED Data)](https://github.com/edithalice/nyc_school_success/blob/master/finance.py)
- [Merging Data](https://github.com/edithalice/nyc_school_success/blob/master/merge_sets.py) - the two data sources were inconsistent in naming practices, making it necessary to use string matching functions to merge the two datasets


## Modeling Process
### Feature Selection
I began the modeling process with approximately 100 model feature from various categories. I eventually chose limit these to numerical features only in the interest of time (I had under two weeks for this project). Even after this limitation though, I still had over 50 features. However, a number of these features overlapped - some overtly, such as subcategories of spending vs categories of spending vs total spending, and some more subtly, such as economic need index vs percent of students receiving free or reduced lunch, etc. For many of these overlapping features, I was hesitant to simply choose one, since the goal of this project was to discover which features were most impactful using data, not necessarily intuition. Therefore, I wrote some function to test adding and removing various features in order to see which had the least impact on the model I was building.
### Modeling
After some experimentation, I decided to use a Yeoman-Johnson power transform to normalize and standardize the data. I used a standard linear regression to create a model. The goal of the model was interpretability, so I eventually narrowed it down to just 12 features.
### Results
I found that the feature with the highest impact on academic success was attendance rate.
### Code
#### Notebooks
- [EDA and Feature Engineering](https://github.com/edithalice/nyc_school_success/blob/master/2.%20Feature%20Exploration%20and%20Engineering.ipynb)
- [Feature Selection and Modeling](https://github.com/edithalice/nyc_school_success/blob/master/3.%20Feature%20Selection%20and%20Model%20Fitting.ipynb)

## Main Tools Used
### Data Acquisition and Cleaning
- Python
- Selenium
- BeautifulSoup
- Pandas
- fuzzywuzzy (string matching)
### Modeling
- Jupyter Notebooks
- Python
- Sci-kit learn
- Statsmodels
- Pandas
- Numpy
- Matplotlib
- Seaborn
- Yellowbrick

## Deliverables
### Notebooks
- [Data Acquisition Process](https://github.com/edithalice/nyc_school_success/blob/master/1.%20Data%20Collection%20and%20Cleaning.ipynb)
- [EDA and Feature Engineering](https://github.com/edithalice/nyc_school_success/blob/master/2.%20Feature%20Exploration%20and%20Engineering.ipynb)
- [Modeling](https://github.com/edithalice/nyc_school_success/blob/master/3.%20Feature%20Selection%20and%20Model%20Fitting.ipynb)
### Python Modules
- [Web Scraping](https://github.com/edithalice/nyc_school_success/blob/master/scrape_nysed.py)
- [Data Cleaning (Quality Review)](https://github.com/edithalice/nyc_school_success/blob/master/success.py)
- [Data Cleaning (NYSED Data)](https://github.com/edithalice/nyc_school_success/blob/master/finance.py)
- [Merging DataFrames](https://github.com/edithalice/nyc_school_success/blob/master/merge_sets.py)
- [Utility Functions](https://github.com/edithalice/nyc_school_success/blob/master/utility_functions.py) (used in EDA and modelling processes)
### Presentation
- [Google Slides](https://docs.google.com/presentation/d/1Jhjqel9jXJb--Zxp2vGh2CEPhIQRUi5mXUQnX2cSLAA/edit?usp=sharing)
- [PDF](https://github.com/edithalice/nyc_school_success/blob/master/presentation.pdf)
