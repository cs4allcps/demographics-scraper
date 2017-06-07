# demographics-scraper
Basic scraper for ECS student information

This tool scrapes sim.cps.k12.il.us for data regarding students in CS4All classes with a focus on students in ECS. It utilizes Selenium PhantomJS webdrivers and BeautifulSoup to navigate the site and find the classes and their students.

### Information Scraped
- Student IDs
- Student schedules
- Student grades
- Student gender and ethnicity

This information is stored in CSV files for each class, and this information is then compiled into files for each school, network, and the entire district.
