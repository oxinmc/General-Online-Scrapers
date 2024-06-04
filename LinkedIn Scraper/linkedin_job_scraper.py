#pip install selenium
#pip install time

import time
import pandas as pd

import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

import re
import nltk
nltk.download()
from nltk.corpus import stopwords, words, wordnet


# Driver's path
path = 'C:/Users/oxin9/Downloads/chromedriver_win32/chromedriver.exe' #Removed 'C:/'
driver = webdriver.Chrome(path)

# Maximize Window
driver.maximize_window() 
driver.minimize_window() 
driver.maximize_window() 
driver.switch_to.window(driver.current_window_handle)
driver.implicitly_wait(10)


# Enter the site
driver.get('https://www.linkedin.com/login');
time.sleep(2)


# Accept cookies
driver.find_element_by_xpath('//*[@id="artdeco-global-alert-container"]/div/section/div/div[2]/button[1]').click()


# User Credentials
    # Reading txt file where we have our user credentials
    # with open('user_credentials.txt', 'r',encoding="utf-8") as file:
    #     user_credentials = file.readlines()
    #     user_credentials = [line.rstrip() for line in user_credentials]

user_name = '**********' #user_credentials[0] # First line
password = '**********' #user_credentials[1] # Second line
driver.find_element_by_xpath('//*[@id="username"]').send_keys(user_name)
driver.find_element_by_xpath('//*[@id="password"]').send_keys(password)
time.sleep(1)

# Login button
driver.find_element_by_xpath('//*[@id="organic-div"]/form/div[3]/button').click()
driver.implicitly_wait(30)


# Access to the Jobs button and click it
# driver.find_element_by_xpath('//*[@id="global-nav"]/div/nav/ul/li[3]/a/div/div/li-icon/svg').click()
# time.sleep(3)
# Go to search results directly via link
driver.get('https://www.linkedin.com/jobs/search/?currentJobId=3406088140&f_E=2%2C3&f_WT=2%2C3&geoId=104738515&keywords=python&location=Ireland&refresh=true')
time.sleep(1)


# Get all links for these offers
links = []

max_page = driver.find_element_by_xpath('/html/body/div[6]/div[3]/div[4]/div/div/main/div/section[1]/div/div[6]/ul/li[10]/button/span').text
print(max_page)


print('Links are being collected now.')
try: 
    for page in range(2, (int(max_page)+1)):
        time.sleep(2)
        jobs_block = driver.find_element_by_class_name('jobs-search-results-list')
        jobs_list= jobs_block.find_elements(By.CSS_SELECTOR, '.jobs-search-results__list-item')
    
        for job in jobs_list:
            all_links = job.find_elements_by_tag_name('a')
            for a in all_links:
                if str(a.get_attribute('href')).startswith("https://www.linkedin.com/jobs/view") and a.get_attribute('href') not in links: 
                    links.append(a.get_attribute('href'))
                else:
                    pass
            # scroll down for each job element
            driver.execute_script("arguments[0].scrollIntoView();", job)
        
        print(f'Collecting the links in the page: {page-1}')
        # go to next page:
        driver.find_element_by_xpath(f"//button[@aria-label='Page {page}']").click()
        time.sleep(3)
except:
    pass

print('Found ' + str(len(links)) + ' links for job offers')


# Create empty lists to store information
job_titles = []
company_names = []
company_locations = []
work_methods = []
post_dates = []
work_times = [] 
job_desc = []

i = 0
j = 1
# Visit each link one by one to scrape the information
print('Visiting the links and collecting information just started.')
for i in range(len(links)):
    try:
        driver.get(links[i])
        i=i+1
        time.sleep(2)
        # Click See more.
        driver.find_element_by_class_name("artdeco-card__actions").click()
        time.sleep(2)
    except:
        pass
    
    # Find the general information of the job offers
    contents = driver.find_elements_by_class_name('p5')
    for content in contents:
        try:
            job_titles.append(content.find_element_by_tag_name("h1").text)
            company_names.append(content.find_element_by_class_name("jobs-unified-top-card__company-name").text)
            company_locations.append(content.find_element_by_class_name("jobs-unified-top-card__bullet").text)
            work_methods.append(content.find_element_by_class_name("jobs-unified-top-card__workplace-type").text)
            post_dates.append(content.find_element_by_class_name("jobs-unified-top-card__posted-date").text)
            work_times.append(content.find_element_by_class_name("jobs-unified-top-card__job-insight").text)
            print(f'Scraping the Job Offer {j} DONE.')
            j+= 1
            
        except:
            pass
        time.sleep(2)
        
        # Scraping the job description
    job_description = driver.find_elements_by_class_name('jobs-description__content')
    for description in job_description:
        job_text = description.find_element_by_class_name("jobs-box__html-content").text
        job_desc.append(job_text)
        print(f'Scraping the Job Offer {j}')
        time.sleep(2)  
            
# Creating the dataframe 
df = pd.DataFrame(list(zip(job_titles,company_names,
                    company_locations,work_methods,
                    post_dates,work_times)),
                    columns =['job_title', 'company_name',
                           'company_location','work_method',
                           'post_date','work_time'])

# Storing the data to csv file
df.to_csv('job_offers.csv', index=False)

# Output job descriptions to txt file
with open('job_descriptions.txt', 'w',encoding="utf-8") as f:
    for line in job_desc:
        f.write(line)
        f.write('\n')


# Creating the dataframe 
df = pd.DataFrame(list(zip(job_titles,company_names,
                    company_locations,work_methods,
                    post_dates,work_times, job_desc)),
                    columns =['job_title', 'company_name',
                           'company_location','work_method',
                           'post_date','work_time', 'job_desc'])

# Storing the data to csv file
df.to_csv('job_offers.csv', index=False)

from collections import Counter

manywords = words.words() + list(wordnet.words())
#manywords = first_list + list(set(second_list) - set(first_list))

# Read the csv file
df = pd.read_csv('job_offers.csv')

i = 0
job_desc_str = ''
for index, row in df.iterrows():
    prep_str = str(row['job_desc']).lower().replace('/', ' ').replace(':', '').replace('.', '').replace(',', '').replace('python', 'py3').replace('!', '')
    desc1 = re.search(r'(?<=looking for someone).*|(?<=what you need).*|(?<=expertise).*|(?<=required).*|(?<=desired).*|(?<=experience).*|(?<=qualifications).*', prep_str)
    try:
        desc2 = desc1[0]
        job_desc_str = job_desc_str + desc2
    except:
        i+=1
        
print('{} slipped through'.format(i))


# split() returns list of all the words in the string
# Pass the split_it list to instance of Counter class.

split_it = job_desc_str.split()
print(type(split_it), len(split_it))

filtered_words1 = [word for word in split_it if word not in stopwords.words('english')] #Pre filter stop words to ease burden on next filtering
print(type(filtered_words1), len(filtered_words1))

filtered_words = [word for word in filtered_words1 if word not in manywords]
print(type(filtered_words), len(filtered_words))
Counter = Counter(filtered_words)

most_occur = Counter.most_common(200)
print(most_occur)


# For Future -> Should look at words that occur only a few times in a job post, but are often present across all postings (?)
