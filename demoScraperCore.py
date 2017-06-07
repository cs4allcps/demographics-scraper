from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, ElementNotVisibleException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import getpass, os, sys, time, datetime, shutil, urllib2, threading, collections, string
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from schools import schools
from networks import networks, nwSchools
from unicodecsv import reader, writer

allSchooldf = pd.DataFrame.from_csv('CPS_Schools.csv')
"""
findSchools()
Input: N/A
Output: schoollist, prettylist

This function allows for users to select a single school from the list of
schools in the SIM database. The schools is returned in a two lists.
schoollist contains the school name in a form that can be used to search against
the SIM site, and prettylist contains the school name in a cleaner form that can
be displayed to the user.
"""
def findSchools():
    print "SCHOOL SEARCH"
    found = False
    schoollist = []
    prettylist = []
    while not found:
        search = raw_input("Search: ")
        # split the search string so that it can search the schools using
        # multiple keywords
        searchStrings = search.split()
        matches = []
        for ss in searchStrings:
            ssmatches = [s for s in schools if ss.lower() in s.lower()]
            matches += ssmatches
        # this eliminates any duplicates from the matches list
        matches = list(set(matches))
        # if multiple matches...
        if len(matches) >= 1:
            for i in range(len(matches)):
                print i, matches[i][:-14]
            print '\nType number of option to select school'
            print 'If schools is not available, simply hit enter and you can search again'
            selection = raw_input("Selection number: ")
            # user did not select school
            if selection == '':
                print "No selection. Search again."
            # user did select school
            elif int(selection) in range(len(matches)):
                selection = matches[int(selection)]
                schoollist.append(selection)
                prettylist.append(selection[:-14]) # = selection[:-14]
                found = True
                print "Selected:",prettylist[0]
                return schoollist, prettylist
            # user selected invalid number
            elif int(selection) < 0 or int(selection) >= len(matches):
                print "Invalid choice number. Seach again."
            print
        else:
            # no schools found
            print 'Did not find any schools related to that search\nPlease try again\n'

"""
fromReportFile(textfile, folder=None)
Input:
textfile - the text file to read schools from
folder - folder to check for duplicate reports
Output: schoollist, prettylist

This function allows users to import a textfile with a list of schools that will
be converted into an array of schools to use while searching against the SIM
site and an array of school names that are in a good form to show to the user.
"""
def fromReportFile(textfile, folder=None):
    print "READING FROM SCHOOL LIST"
    schoollist = []
    prettylist = []
    filelist = []

    # if there is a folder provided, find the files within it
    if folder:
        filelist = [f for f in os.listdir(folder)
                        if os.path.isfile(os.path.join(folder,f))]

    # read through the textfile to build school list
    with open(textfile) as f:
        lines = f.readlines()
        for i in range(len(lines)):
            include = True
            school = lines[i]
            if folder:
                for f in filelist:
                    if school.strip() + ".csv" in f:
                        include = False
                        break
            if include:
                schoollist.append(lines[i].replace("\n", " - School View"))
                prettylist.append(lines[i].rstrip("\n"))
            include = True

    return schoollist, prettylist

"""
testLogin()
Input:
chrome - boolean that dictates whether the driver will be a chrome or PhantonJS driver
Output: username, password

This function asks the user to provide a username and password to login to the
SIM website. If either the username or password are wrong, then it will allow
the user to try again. If the username and password are correct, then the
function will return the username and password.
"""
def testLogin(chrome = False):
    loggedIn = False
    # if not logged in, loop until user provides legitimate login information
    while not loggedIn:
        user = raw_input("USERNAME: ")
        password = getpass.getpass("PASSWORD: ")

        # create driver
        # create chrome driver
        if chrome:
            driver = webdriver.Chrome()
        # or create headless driver
        else:
            driver = webdriver.PhantomJS()
            driver.set_window_size(1124, 5000)

        # go to SIM login page
        driver.get("http://sim.cps.k12.il.us/")

        # LOGIN PAGE
        print "\nAttempting to sign in"
        attempted = False
        # sometimes the site does not load properly and doesn't give the driver
        # a chance to ever log in
        while not attempted:
            try:
                elem = driver.find_element_by_name("user")
                elem.clear()
                elem.send_keys(user)
                # password
                elem = driver.find_element_by_name("pass")
                elem.clear()
                elem.send_keys(password)
                # domain
                elem = driver.find_element_by_name("domn")
                elem.clear()
                elem.send_keys("ADMIN")
                elem.send_keys(Keys.RETURN)
                attempted = True
            # login page didn't load properly, try again
            except NoSuchElementException:
                attempted = False

        # check for error message
        try:
            driver.find_element_by_id("errmsg")
            # if error message exists, then close window and ask for new login info
            print "Incorrect username or password"
            driver.quit()
        except NoSuchElementException:
            # error message does not exist and the user has logged in
            print "Logged in\n"
            loggedIn = True
            driver.quit()
            # return correct login info
            return user, password

"""
login(user, password)
Input:
user - username
password - user's password
chrome - boolean that dictates whether the driver will be a chrome or PhantonJS driver

Output: driver
driver - Selenium webdriver that is logged into the SIM site
"""
def login(user, password, chrome=False):
    # initialize driver
    if chrome:
        driver = webdriver.Chrome()
    else:
        driver = webdriver.PhantomJS()
        driver.set_window_size(1124, 5000)

    # go to login page
    driver.get("http://sim.cps.k12.il.us/")

    # LOGIN PAGE
    print "\nSigning in"
    loggedin = False

    # somtimes the login page does not load properly, so this will loop until
    # the login page can be correctly loaded
    while not loggedin:
        try:
            # username
            elem = driver.find_element_by_name("user")
            elem.clear()
            elem.send_keys(user)
            # password
            elem = driver.find_element_by_name("pass")
            elem.clear()
            elem.send_keys(password)
            # domain
            elem = driver.find_element_by_name("domn")
            elem.clear()
            elem.send_keys("ADMIN")
            elem.send_keys(Keys.RETURN)
            loggedin = True
        except NoSuchElementException:
            loggedin = False
    print "Signed in"
    # return driver with SIM page properly logged into
    return driver

"""
This is a class for thread generation. This can be used when you want
to run multiple threads to download multiple sets of reports at the same time.
"""
class sThread(threading.Thread):
    def __init__(self, threadID, user, password, prettylist, schoollist, folder, dt, printLock, chrome=False):
        threading.Thread.__init__(self)
        # thread ID
        self.threadID = threadID
        # username
        self.user = user
        # password
        self.password = password
        # list of schools:
        # in printable format
        self.prettylist = prettylist
        # in searchable format
        self.schoollist = schoollist
        # general download folder
        self.folder = folder
        # download time
        self.dt = dt
        # printing lock
        self.printLock = printLock
        # boolean that decides if driver should be chrome or PhantomJS
        self.chrome = chrome

    # function that initializes the thread
    def run(self):
        with self.printLock:
            print "Starting " + str(self.threadID)
        scraperThread(self.threadID, self.user, self.password, self.prettylist,
                        self.schoollist, self.folder, self.dt, self.printLock, self.chrome)
        with self.printLock:
            print "Exiting " + str(self.threadID)

"""
scraperThread(n, user, password, prettylist, schoollist, folder, downloadTime, chrome)
Input:
n - thread ID
user - username
password - user's password
prettylist - list of schools to iterate through stored in printable format
schoollist - list of schools to iterate through stored in searchable format
folder - download destination folder
chrome - boolean that dictates whether the driver will be a chrome or PhantonJS driver

Output: N/A

This function handles the scraping of the schools listed in schoollist. It
stores demographic information about students in the ECS classes the schools. It
also stores scheduling information for each of those students.
"""
def scraperThread(n, user, password, prettylist, schoollist, folder, downloadTime, printLock, chrome):
    driver = login(user, password, chrome)
    charts = False

    for i in range(len(schoollist)):
        pretty = prettylist[i]
        selection = schoollist[i]
        # ROLE SELECTION
        with printLock:
            print n,"-","Selecting " + pretty

        if selection in schools:
            schoolIndex = schools.index(selection)
            attemptCount = 0
            while True:
                attemptCount += 1
                try:
                    # navigates to role page
                    driver.get("https://sim.cps.k12.il.us/PowerSchoolSMS/User/SwitchRole.aspx?Mode=SwitchRole&reset=true")
                    # search schools for selection
                    schoolsInputs = driver.find_elements_by_name("SelectedRole")
                    # value = schoolsInputs[schoolIndex].get_attribute("value")
                    value = schoolsInputs[schoolIndex].get_attribute("value")
                    break
                except:
                    with printLock:
                        print n,selection,"Issue with value index"
                    if attemptCount > 10:
                        break

            # select school
            driver.find_element_by_css_selector("input[type='radio'][value='"+value+"']").click()
            # click OK and submit
            driver.find_element_by_name("TP$QAID_cmd_ok").click()
            # navigate to class page
            driver.get("https://sim.cps.k12.il.us/PowerSchoolSMS/Class/ClassesList.aspx?reset=true")
            while True:
                try:
                    driver.find_element_by_id("TP_QAID_QuickSearchSection_IMG").click()
                    break
                except ElementNotVisibleException:
                    with printLock:
                        print n,selection, "issues with TP_QAID_QuickSearchSection_IMG"
            # select 'Course number' option
            driver.find_element_by_xpath("//select[@name='TP$QAID_ClassSearchControl_Tab$Field0']/option[text()='Course number']").click()
            # select 'contains' option
            driver.find_element_by_xpath("//select[@name='TP$QAID_ClassSearchControl_Tab$Field0_Operator']/option[text()='contains']").click()

            rowCount = 0
            i = 0
            # possible class numbers for ECS
            classNumbers = ["66820", "71970", "668201"]
            while rowCount <= 2:
                # insert class number
                elem = driver.find_element_by_name("TP$QAID_ClassSearchControl_Tab$Field0_TextBox")
                elem.clear()
                elem.send_keys(classNumbers[i])
                elem.send_keys(Keys.RETURN)
                i += 1
                # sleep while infomation loads
                # TODO: find better method
                time.sleep(10)
                # access html on page
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                # access class table on page
                tableSoup = soup.find('table', attrs={'id':'TP_QAID_ClassGrid'})
                # isolate the rows
                rows = tableSoup.find_all('tr')
                # rowCount == number of classes found
                rowCount = len(rows)
                # break while loop if all course numbers have been searched for
                if i >= len(classNumbers):
                    break

            # remove the top and bottom rows (contain)
            rows = rows[1:len(rows)-1]
            # create directory for data
            directory = folder + '//' + downloadTime + ' ' + pretty + '/'
            # set to true if directory already exists
            if not os.path.exists(directory):
                os.makedirs(directory)

            # iterate through classes previously found
            for i in range(len(rows)):
                # isolate row
                rowSoup = rows[i]
                # find attributes from row
                attrs = rowSoup.find_all('td')
                # isolate the section name
                section = attrs[1].text.encode('utf-8').translate(string.maketrans("",""), string.punctuation)
                # isolate teacher of class
                teacher = attrs[2].text
                # isolate semester
                term = attrs[3].text
                # isoalte class period
                period = attrs[4].text
                # isolate number of students?
                num = attrs[6].text
                # create file for class
                fname = directory + term + ' ' + section + ' ' + teacher + ' ' + period+ '.csv'
                with printLock:
                    print n,"-",section, teacher, term, period, num
                # check if class if from the first or second semester
                firstTerm = True
                if '2' in term:
                    firstTerm = False

                # file already exists => skip to next class
                if os.path.isfile(fname):
                    continue
                # create class directory if it does not already exist
                if not os.path.exists(directory + section + '/'):
                    os.makedirs(directory + section + '/')

                # isolate link to class page
                href = rowSoup.find('td', attrs={'col':"2"}).find('a', href=True)['href']
                href = href.split("'")[1].split("%")[0]
                # direct driver to class page
                driver.get("https://sim.cps.k12.il.us/" + href)
                # grab page html
                studentSoup = BeautifulSoup(driver.page_source, 'html.parser')
                # isolate table with student information
                studentTable = studentSoup.find('table', attrs={'id' : 'TP_QAID_StudentGrid'})
                # if the table exists...
                if studentTable:
                    # find all student rows
                    students = studentTable.find_all('tr')
                    topRow = students[0]
                    secondRow = students[1]
                    try:
                        classname = secondRow.find_all('td')[2]
                    except IndexError:
                        continue
                    with printLock:
                        print n,"-",classname.text.strip()
                    # remove top, bottom rows with column information
                    students = students[1:len(students)-1]
                    # find information available in columns from the top row
                    infoAvailable = topRow.find_all('td')
                    success = True
                    # iterate through rows and pages to find all students in the class
                    while success:
                        try:
                            element = driver.find_element_by_id("TP_QAID_StudentGrid_NextID")
                            if element.value_of_css_property('color') != "rgba(128, 128, 128, 1)":
                                element.click()
                                studentSoup = BeautifulSoup(driver.page_source, 'html.parser')
                                studentTable = studentSoup.find('table', attrs={'id' : 'TP_QAID_StudentGrid'})
                                extraStudents = studentTable.find_all('tr')
                                students += extraStudents[1:len(extraStudents)-1]
                            else:
                                success = False
                        except NoSuchElementException:
                            success = False
                        except AttributeError:
                            success = False

                    # check if
                    gndr = 0
                    ethc = 0
                    grd = 0
                    lng = 0
                    nm = 1

                    for i in range(len(infoAvailable)):
                        col = infoAvailable[i].text
                        col = col.split(" ")[0]

                        if col == "Gender":
                            gndr = i
                        elif col == "Ethnic":
                            ethc = i
                        elif col == "Gr(A)":
                            grd = i
                        # elif col == "Language":
                        #     lng = i
                        elif col == "Student":
                            nm = i
                    print
                    gender = []
                    ethnic = []
                    grade = []
                    language = []
                    grade_level = []
                    class_grade = []
                    student_id = []
                    # first semester grades
                    grade_1RC = []
                    grade_FS = []
                    grade_1PR = []
                    grade_2PR = []
                    # second semester grades
                    grade_3RC = []
                    grade_SS = []
                    grade_3PR = []
                    grade_4PR = []

                    for s in students:
                        sattrs =  s.find_all('td')
                        # isolate student href
                        slink = sattrs[nm].find('a', href=True)
                        href = slink['href'].split("'")[1].split("&")[0]
                        # go to student page
                        driver.implicitly_wait(10)
                        driver.get("https://sim.cps.k12.il.us/" + href)
                        # find student grade level
                        element = driver.find_element_by_id("ibar")
                        sgrade_level = element.find_elements_by_class_name("pager-info")[0].text
                        with printLock:
                            print n, "-", sgrade_level
                        sid = sgrade_level.split(",")[0]
                        sgrade_level = sgrade_level.split("-")[1].split(",")[0]
                        # add student grade level to grade_level
                        grade_level.append(sgrade_level)
                        student_id.append(sid)

                        # go to class grades page
                        cg = driver.find_element_by_id("QAID_Grades")
                        cg.click()

                        # Show all 8 grade reports
                        allReports = driver.find_element_by_id('TP_ctl30_QAID_StudentGradesGrid_QAID_NumberOfGradeColumnsList')
                        allReportsSelect = Select(allReports)
                        allReportsSelect.select_by_visible_text("8")

                        # Select First or Second Semester
                        report = driver.find_element_by_id('TP_ctl30_QAID_StudentGradesGrid_QAID_GradingPeriodList')
                        reportSelect = Select(report)
                        if firstTerm:
                            reportSelect.select_by_visible_text("First Semester")
                        else:
                            reportSelect.select_by_visible_text("Second Semester")
                        # isolate grades table
                        try:
                            cgtable = driver.find_element_by_id("TP_ctl30_QAID_StudentGradesGrid")
                            cgsoup = BeautifulSoup(cgtable.get_attribute("innerHTML"), 'html.parser')
                            cgrows = cgsoup.find_all('tr')
                            cgrows = cgrows[1:len(cgrows)-1]

                            student_grades = {}
                            student_classes = []
                            # first Semester grades
                            student_1RC = []
                            student_FS = []
                            student_1PR = []
                            student_2PR = []
                            # second semester grades
                            student_3RC = []
                            student_SS = []
                            student_3PR = []
                            student_4PR = []

                            for cgr in cgrows:
                                cgtd = cgr.find_all('td')
                                cgclass = cgr.find_all('td')[0].text.strip()
                                cgletter = cgr.find_all('td')[1].text.strip()
                                # print 'cgletter:',cgletter
                                if cgclass != 'Comments' and cgclass != 'Default':
                                    student_classes.append(cgclass)
                                    if firstTerm:
                                        student_1RC.append(cgtd[1].text.strip())
                                        student_FS.append(cgtd[2].text.strip())
                                        student_1PR.append(cgtd[5].text.strip())
                                        student_2PR.append(cgtd[6].text.strip())
                                    else:
                                        student_3RC.append(cgtd[3].text.strip())
                                        student_SS.append(cgtd[4].text.strip())
                                        student_3PR.append(cgtd[7].text.strip())
                                        student_4PR.append(cgtd[8].text.strip())

                                # TODO: find better method for removing the punctuation
                                if cgclass in section or section.split('-')[0].replace(".", "") in cgclass or cgclass in classname:
                                    class_grade.append(cgletter)
                                    if firstTerm:
                                        # print n,"-","1RC:",cgtd[1].text.strip()
                                        grade_1RC.append(cgtd[1].text.strip())
                                        grade_FS.append(cgtd[2].text.strip())
                                        grade_1PR.append(cgtd[5].text.strip())
                                        grade_2PR.append(cgtd[6].text.strip())
                                    else:
                                        grade_3RC.append(cgtd[3].text.strip())
                                        grade_SS.append(cgtd[4].text.strip())
                                        grade_3PR.append(cgtd[7].text.strip())
                                        grade_4PR.append(cgtd[8].text.strip())
                        # if grades table does not exist => append None where the grade would be
                            student_grades['class'] = student_classes
                            if firstTerm:
                                student_grades['1RC'] = student_1RC
                                student_grades['FS'] = student_FS
                                student_grades['1PR'] = student_1PR
                                student_grades['2PR'] = student_2PR
                            else:
                                student_grades['3RC'] = student_3RC
                                student_grades['SS'] = student_SS
                                student_grades['3PR'] = student_3PR
                                student_grades['4PR'] = student_4PR
                            gradesdf = pd.DataFrame(student_grades)
                            cols = gradesdf.columns.tolist()
                            cols = cols[-1:] + cols[:-1]
                            gradesdf = gradesdf[cols]
                            gradesdf = gradesdf.set_index('class')
                            if firstTerm:
                                gradescsv = str(sid) + '-1.csv'
                            else:
                                gradescsv = str(sid) + '-2.csv'

                            gradesdf.to_csv(directory + section + '/' + gradescsv)

                        except NoSuchElementException:
                            class_grade.append(None)

                        # return to class page
                        #driver.back()

                        if gndr:
                            gender.append(sattrs[gndr].text)
                        if ethc:
                            ethnic.append(sattrs[ethc].text)
                        if grd:
                            grade.append(sattrs[grd].text)
                        if lng:
                            language.append(sattrs[lng].text)

                    studentDict = dict()
                    if gndr:
                        studentDict['gender'] = gender
                        plotDict = {}
                        for g in gender:
                            if g in plotDict.keys():
                                plotDict[g] += 1
                            else:
                                plotDict[g] = 0

                    if ethc:
                        studentDict['ethnicity'] = ethnic
                        plotDict = {}
                        for e in ethnic:
                            if e in plotDict.keys():
                                plotDict[e] += 1
                            else:
                                plotDict[e] = 0

                    if grd:
                        studentDict['grade'] = grade
                        plotDict = {}
                        for g in grade:
                            if g in plotDict.keys():
                                plotDict[g] += 1
                            else:
                                plotDict[g] = 0

                    if lng:
                        # studentDict['language'] = language
                        plotDict = {}
                        for lang in language:
                            if lang in plotDict.keys():
                                plotDict[lang] += 1
                            else:
                                plotDict[lang] = 0

                    if class_grade:
                        # studentDict['class_grade'] = class_grade
                        plotDict = {}
                        for cg in class_grade:
                            if cg in plotDict.keys():
                                plotDict[cg] += 1
                            else:
                                plotDict[cg] = 0

                    studentDict['grade_level'] = grade_level
                    studentDict['id'] = student_id
                    if firstTerm: #if len(grade_1RC):
                        studentDict['1RC'] = grade_1RC
                        studentDict['FS'] = grade_FS
                        studentDict['1PR'] = grade_1PR
                        studentDict['2PR'] = grade_2PR
                    else:
                        studentDict['3RC'] = grade_3RC
                        studentDict['SS'] = grade_SS
                        studentDict['3PR'] = grade_3PR
                        studentDict['4PR'] = grade_4PR

                    with printLock:
                        print n,"-","grade_1RC"
                        print n,"-",grade_1RC
                        for key in studentDict.keys():
                            print key, len(studentDict[key])

                    try:
                        studentdf = pd.DataFrame(studentDict)
                        cols = studentdf.columns.tolist()
                        cols = cols[-1:] + cols[:-1]
                        studentdf = studentdf[cols]
                        studentdf = studentdf.set_index('id')
                        # classdfs[section] = studentdf

                        studentdf.to_csv(fname)
                        with printLock:
                            print n,"-",selection,"Demographics"
                            print studentdf
                            print
                    except ValueError:
                        with printLock:
                            print n,"-",fname,"failed due to missing grades"
                    # allDf.append(studentdf)

"""
findNetwork(school)
Input:
school - will find network of this school

Output:
network - network of input school
"""
def findNetwork(school):
    return allSchooldf[allSchooldf['School Long Name'] == school]['Network'].values[0]

"""
schoolsInNetwork(network)
Input:
network - input netowrk

Output:
schools - schools within the input network
"""
def schoolsInNetwork(network):
    schools = networks[network]
    return schools

"""
calibrateNetworks()
Input: N/A

Output: N/A

Updates networks.py which includes information on which schools
are in which network.
"""
def calibrateNetworks():
    print "Updating networks.py"
    # access CPS school csv
    allSchooldf = pd.DataFrame.from_csv('CPS_Schools.csv')

    networks = {}
    nwSchools = {}
    for s in schools:
        s = s.replace(" - School View", "")
        try:
            nw = allSchooldf[allSchooldf['School Long Name'] == school]['Network'].values[0]
        except IndexError:
            nw = None

        if nw not in networks:
            networks[nw] = [s]
        else:
            networks[nw].append(s)

        nwSchools[s] = nw

    with open("networks.py", "w") as f:
        f.write("networks = " + str(networks) + '\n\n')
        f.write("nwSchools = " + str(nwSchools))
        f.close()

    print "networks.py updated"

"""
calibrateSchools() updates schools.py, which contains a list that allows you to
easily interface with the school selection area of the sim.cps.k12.il.us website.
"""
def calibrateSchools(user, password):

    driver = login(user, password)

    # navigate to role page
    driver.get("https://sim.cps.k12.il.us/PowerSchoolSMS/User/SwitchRole.aspx?Mode=SwitchRole&reset=true")
    #select schools
    schools = driver.find_elements_by_class_name("last-col")
    networks = collections.defaultdict(list)
    print "Reading schools"
    for i in range(1,len(schools)):
        element = schools[i]
        schools[i] = element.text

    del schools[0]
    print "Closing window"
    driver.quit()
    print "Updating schools.py"
    with open("schools.py", "w") as f:
        f.write("schools = " + str(schools))
        f.close()

    # return driver

'''
reportMerge() merges records scraped from sim.cps.k12.il.us and compiles them
into files. it also makes summary files from the merged files.
'''
def reportMerge(folder, ECS=True):

    date = folder.split(' ')[0]
    folderlist = os.listdir(folder)

    nwFolder = folder + date + ' Network Reports\\'
    if not os.path.isdir(nwFolder):
        os.mkdir(nwFolder)

    # setup storage for merge and summary file locations
    fsMergeFiles = []
    ssMergeFiles = []
    fsNetworkMergeFiles = collections.defaultdict(list)
    ssNetworkMergeFiles = collections.defaultdict(list)


    # file names for merge and summary files
    fsmf = date + " ECS MergeFile S1.csv"
    ssmf = date + " ECS MergeFile S2.csv"
    fssf = date + " ECS Summary S1.csv"
    sssf = date + " ECS Summary S2.csv"

    if not ECS:
        fsmf = date + " MergeFile S1.csv"
        ssmf = date + " MergeFile S2.csv"
        fssf = date + " Summary S1.csv"
        sssf = date + " Summary S2.csv"

    # iterate through semesters
    for i in [1,2]:
        mergeFiles = []
        nwMergeFiles = collections.defaultdict(list)

        sem = 'S' + str(i)
        AP = 'AP' + str(i)
        if i == 1:
            demos = ['ethnicity', 'gender', 'grade_level', "1PR", "1RC", "2PR", "FS"]
            row = ["id", "1PR", "1RC", "2PR", "FS", "ethnicity", "gender", "grade_level"]
            mf = date + " S1 ECS MergeFile.csv"
            sf = date + " S1 ECS Summary.csv"
            districtmf = folder + date + " S1 District ECS MergeFile.csv"
            districtsf = folder + date + " S1 District ECS Summary.csv"
            if not ECS:
                mf = date + " S1 MergeFile.csv"
                sf = date + " S1 Summary.csv"
                districtmf = folder + date + " S1 District MergeFile.csv"
                districtsf = folder + date + " S1 District Summary.csv"
        else:
            demos = ['ethnicity', 'gender', 'grade_level', "3PR", "3RC", "4PR", "SS"]
            # demos = ["id", "3PR", "3RC", "4PR", "SS", "ethnicity", "gender", "grade_level"]
            row = ["id", "3PR", "3RC", "4PR", "SS", "ethnicity", "gender", "grade_level"]
            mf = date + " S2 ECS MergeFile.csv"
            sf = date + " S2 ECS Summary.csv"
            districtmf = folder + date + " S2 District ECS MergeFile.csv"
            districtsf = folder + date + " S2 District ECS Summary.csv"
            if not ECS:
                mf = date + " S2 MergeFile.csv"
                sf = date + " S2 Summary.csv"
                districtmf = folder + date + " S2 District MergeFile.csv"
                districtsf = folder + date + " S2 District Summary.csv"

        ##############################################
        ############ GENERATE MERGE FILES ############
        ##############################################

        # School Merge Files
        for fldr in folderlist:
            # ignore prior merge files
            if 'MergeFile' in fldr or 'All Schools' in fldr or 'Network Reports' in fldr or 'Summary' in fldr:
                continue
            # find current school from folder name
            school = fldr.split(' ', 1)[1]
            print school

            # collect first semester files
            filelist = [f for f in os.listdir(folder + fldr)
                                if os.path.isfile(os.path.join(folder + fldr,f)) and '.csv' in f and sem in f]

            # ignore school merge and summary files
            if mf in filelist:
                filelist.remove(mf)
            if sf in filelist:
                filelist.remove(sf)

            # add mergefile to list of network merge files
            if school in nwSchools:
                nw = nwSchools[school]
                nwMergeFiles[nw].append(folder + fldr + '\\' + mf)

            with open(folder + fldr + '\\' + mf, "wb") as o:
                gal = writer(o)
                gal.writerow(row)

                for fl in filelist:
                    with open(folder + fldr + '\\' + fl, "r") as f:
                        # if class is an AP but only looking for ECS classes => skip
                        if AP in fl and ECS:
                            continue
                        # copy lines to merge file
                        for line in f.readlines():
                            if 'gender' in line:
                                continue
                            gal.writerow(line.strip().split(','))

            # add to list of first semester merge files
            mergeFiles.append(folder+ fldr + '\\' + mf)
            # df = pd.DataFrame.from_csv(folder + fldr + '\\' + mf)

        # Districte Merge File
        with open(districtmf, "wb") as o:
            gal = writer(o)
            gal.writerow(row)

            for fl in mergeFiles:
                with open(fl, "r") as f:
                    for line in f.readlines():
                        if 'gender' in line:
                            continue
                        gal.writerow(line.strip().split(',')[:8])

        for nw in networks:
            schools = networks[nw]

            if nw:
                nwmf = nwFolder + date + ' ' + sem + ' ' + nw + ' ECS MergeFile.csv'
                if not ECS:
                    nwmf = nwFolder + date + ' ' + sem + ' ' + nw + ' MergeFile.csv'

                with open(nwmf, "wb") as o:
                    gal = writer(o)
                    gal.writerow(row)

                    for fl in nwMergeFiles[nw]:
                        with open(fl, "r") as f:
                            for line in f.readlines():
                                if 'gender' in line:
                                    continue
                                gal.writerow(line.strip().split(','))


        ##############################################
        ########### GENERATE SUMMARY FILES ###########
        ##############################################

        for fl in mergeFiles:
            filenameinfo = fl.split('\\')
            newsf = filenameinfo[0] + '\\' + filenameinfo[1] + '\\' + sf
            df = pd.DataFrame.from_csv(fl)
            total = len(df.index)
            with open(newsf, "wb") as o:
                gal = writer(o)
                gal.writerow(["demo", "cat", "percent", "num", "total"])

                for dm in demos:
                    catlist = df[dm].tolist()
                    catset = set(catlist)
                    catcounter = collections.Counter(catlist)
                    for cat in catset:
                        num = catcounter[cat]
                        if total > 0 :
                            percent = num/float(total)
                        else:
                            percent = 0
                        gal.writerow([dm, cat, percent, num, total])

        df = pd.DataFrame.from_csv(districtmf)
        total = len(df.index)
        with open(districtsf, "wb") as o:
            gal = writer(o)
            gal.writerow(["demo", "cat", "percent", "num", "total"])

            for dm in demos:
                catlist = df[dm].tolist()
                catset = set(catlist)
                catcounter = collections.Counter(catlist)
                for cat in catset:
                    num = catcounter[cat]
                    if total > 0:
                        percent = num / float(total)
                    else:
                        percent = 0
                    gal.writerow([dm, cat, percent, num, total])

        for nw in networks:

            if nw:
                nwmf = nwFolder + date + ' ' + sem + ' ' + nw + ' ECS MergeFile.csv'
                nwsf = nwFolder + date + ' ' + sem + ' ' + nw + ' ECS Summary.csv'
                if not ECS:
                    nwsf = nwFolder + date + ' ' + sem + ' ' + nw + ' Summary.csv'
                    nwmf = nwFolder + date + ' ' + sem + ' ' + nw + ' MergeFile.csv'

            # df = pd.DataFrame.from_csv(nwmf, usecols=row)
            df = pd.read_csv(nwmf, usecols=row)
            total = len(df.index)

            with open(nwsf, "wb") as o:
                gal = writer(o)
                gal.writerow(["demo", "cat", "percent", "num", "total"])

                for dm in demos:
                    catlist = df[dm].tolist()
                    catset = set(catlist)
                    catcounter = collections.Counter(catlist)
                    for cat in catset:
                        num = catcounter[cat]
                        if total > 0:
                            percent = num / float(total)
                        else:
                            percent = 0
                        gal.writerow([dm, cat, percent, num, total])
