# demographics-scraper
Basic scraper for ECS student information

This tool scrapes sim.cps.k12.il.us for data regarding students in CS4All classes with a focus on students in ECS. It utilizes Selenium PhantomJS webdrivers and BeautifulSoup to navigate the site and find the classes and their students.

### Information Scraped
- Student IDs
- Student schedules
- Student grades
- Student gender and ethnicity

This information is stored in CSV files for each class, and this information is then compiled into files for each school, network, and the entire district.

### Dependencies
- Python 2.7 (modules: bs4, collections, datetime, getpass, matplotlib, numpy, os, pandas, selenium, shutil, string, sys, threading, time, unicodecsv, urllib2)
- Selenium
- PhantomJS Webdriver
- Chrome Webdriver
- BeautifulSoup

### Includes
- demoScraper.py: main executable for scraping
- demoScraperCore.py: contains all of the functions for scraping as well as additional functions that could be used later
- cs4allHS.txt: list of high schools in the CS4All program; used for querying schools in SIM
- schools.py, networks.py: files used to speed up querying and record merging
- CPS_Schools.csv, schoolSizes.csv: files used for additional demographic information

### How to Run
Use the following command:

`python demoScraper.py -t <textfile> -tc <thread count> -dt <download time>`
    
- textfile: File to read schools from
- thread count: number of threads to use
- download time: what date you'd like the download to be associated with (also useful for rescraping and depositing records into an old folder where those records may have been skipped initially)
