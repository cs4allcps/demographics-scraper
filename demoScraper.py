from demoScraperCore import fromReportFile, findSchools, testLogin, sThread, calibrateSchools, reportMerge
import argparse, os, datetime, numpy, time, threading
from networks import networks

parser = argparse.ArgumentParser(description="This script does stuff")
parser.add_argument('-t', dest='reportFile', type=str, metavar="<reportfile.txt>",
                    help="This textfile contains the list of schools that the script finds reports for", default=None)
parser.add_argument('-tc', dest='threadCount', type=int, metavar="<max thread count>",
                    help="The number of threads to use", default=2)
parser.add_argument('-c', dest='chrome', action="store_true",
                    help="Run with chrome", default=False)

parser.add_argument('-dt', dest='downloadTime', default=datetime.datetime.now().strftime('%Y-%m-%d'))

args = parser.parse_args()
reportFile = args.reportFile
threadCount = args.threadCount
downloadTime = args.downloadTime
chrome = args.chrome

printLock = threading.Lock()

# downloadTime = datetime.datetime.now().strftime('%Y-%m-%d')
# downloadTime = "2017-06-01"
folder = downloadTime + ' ' + 'ECS Demographics'
schoollist = []
prettylist = []

# if folders do not exists, make them
if not os.path.exists(folder):
    os.makedirs(folder)

user, password = testLogin()
calibrateSchools(user,password)

if reportFile:
    schoollist, prettylist = fromReportFile(reportFile, folder)
else:
    schoollist, prettylist = findSchools()

if len(schoollist) > 1:
    schoolThreadList = numpy.array_split(numpy.array(schoollist), threadCount)
    prettyThreadList = numpy.array_split(numpy.array(prettylist), threadCount)
else:
    threadCount = 1
    schoolThreadList = [schoollist]
    prettyThreadList = [prettylist]

threads = []
for i in range(threadCount):
    thread = sThread(i, user, password, prettyThreadList[i], schoolThreadList[i], folder, downloadTime, printLock, chrome)
    thread.start()
    threads.append(thread)

for i in range(threadCount):
    threads[i].join()

print "Running Again to Check for Missing Schools"
threadCount -= 1
if threadCount < 1:
    threadCount = 1

threads = []
for i in range(threadCount):
    thread = sThread(i, user, password, prettyThreadList[i], schoolThreadList[i], folder, downloadTime, printLock, chrome)
    thread.start()
    threads.append(thread)

for i in range(threadCount):
    threads[i].join()

print "THREADS COMPLETE"

reportMerge(folder + '\\')

for nw in networks:
    networkSuccessReport(folder + '\\', nw)
