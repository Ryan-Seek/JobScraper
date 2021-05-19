import sys
import urllib
import requests
import re
import time
from bs4 import BeautifulSoup
import pandas as pd


## Globals 

avoid_jobs = ["intern", "senior", "Sr.", "Sr", "Sr. ", "principal", "staff", "contract", "II", "2", "III", "3", "mentor", "mentorship", "mechanical", "areospace", "civil"]#job titles to avoid
must_have = ["programmer", "software", "engineer", "developer", "computer", "science"]#must have keywords
position = "Software Engineer 1"#job search title
exp_regex = re.compile('[2-9]\s*\+?-?\s*[1-9]?\s*[yY]e?a?[rR][Ss]?')#regex for phrases like 1+ years, 2+years, etc
max_results = 400 #max results to search through






def scrape_jobs(website, location, filename="foundjobs.xlsx"):    

    tic = time.perf_counter()
    
    if website == 'Indeed':
      jobs_list, listings_count = extract_indeed_job_info(location)
        
    store_jobs(jobs_list, filename)
    toc = time.perf_counter()

    print('{} new postings retrieved from {}.'.format(listings_count, website))
    print(f"Scraped and compiled jobs in {toc - tic:0.4f} seconds")






#basic utility functions

def store_jobs(jobs_list, filename):
  pd.DataFrame(jobs_list).to_excel(filename)#convert dataframe to excel doc


def use_job(title): #checks to see if the job has the required keywords and does not contain the keywords to avoid

  if any(word.lower() in title.lower() for word in must_have):#checks to see if the must have keywords exist

    for word in avoid_jobs:
      if word.lower() in title.lower(): return False#has exclusion words
      
    return True#keywords exist and does not have any exclusion words
  return False#does not include must have keywords

def check_description(description):
  if not exp_regex.search(description):#if description is free of the year requirements then return true
      return True
  return False



##Indeed functions

def load_indeed_divs(location, start): 
    base_url = "https://www.indeed.com/jobs?q=Software+Engineer+I&l={}&sort=date&fromage=last&start={}"
    url = base_url.format(location, start)#creates url with location and page start num

    page = requests.get(url)
    
    soup = BeautifulSoup(page.content, "html.parser")
    job_soup = soup.find(id="resultsCol")#get results part of the page
    
    return job_soup

def extract_indeed_job_info(location):
    
    
    cols = []
    extracted_info = []
    titles= []
    companies = []
    links = []
    dates = []

    cols.append('Titles')
    cols.append('Companies')
    cols.append('Links')
    cols.append('Date Posted')

    for page in range(0, max_results, 10):    #main loop that goes through the pages of results
      job_soup = load_indeed_divs(location, page)
      job_elems = job_soup.find_all('div', class_='jobsearch-SerpJobCard')#gets all jobs on page

      
      updated = False#data updated variable
      
      
      
      for job_elem in job_elems:#go through each job
          title = extract_title_indeed(job_elem)

          if use_job(title):#check to see if title is allowed        
            description = extract_job_desc_indeed(job_elem)
    
            if check_description(description):#check to see if description makes the job invalid
              titles.append(title)
              companies.append(extract_company_indeed(job_elem))
              links.append(extract_link_indeed(job_elem))
              dates.append(extract_date_indeed(job_elem))
              updated = True
      
      if (updated == True):#prevents empty entries from being added
        extracted_info.append(titles)
        extracted_info.append(companies)
        extracted_info.append(links)
        extracted_info.append(dates)
        


      time.sleep(1)#slow down repeated requests to limit timeout 


    jobs_list = {}

    for j in range(len(cols)):#go through extracted data and store into one list
        jobs_list[cols[j]] = extracted_info[j]

    num_listings = len(extracted_info[0])
 
    return jobs_list, num_listings


def extract_title_indeed(job_elem):
    title_elem = job_elem.find('h2', class_='title')
    return title_elem.text.strip().replace('\nnew', '')#return job title without the newline in the string

def extract_job_desc_indeed(job_elem):
    desc_elem = job_elem.find('div', class_='summary')
    return desc_elem.get_text().strip()#return job description

def extract_company_indeed(job_elem):
    company_elem = job_elem.find('span', class_='company')
    return company_elem.text.strip()#return company

def extract_link_indeed(job_elem):
    return 'www.Indeed.com' +job_elem.find('a')['href']#return specific job link

def extract_date_indeed(job_elem):
    date_elem = job_elem.find('span', class_='date')
    return  date_elem.text.strip()#return date posted



   
    
if __name__ == "__main__":
    
    scrape_jobs("Indeed", "Seattle")