from selenium import webdriver
from selenium.webdriver.support.select import Select
from lxml import etree
import time
import re
import os
import csv


def DataOrganizer(coursedata):
    coursesessions = []
    while(len(coursedata) > 8):
        if(coursedata[0]=='@' or coursedata[8][0]=="*"):
            coursesessions.append(coursedata[0:9])
            coursedata = coursedata[9:]

        else:
            coursesessions.append(coursedata[0:8])
            coursedata = coursedata[8:]
    return coursesessions

def CreatePath():
    print("Welcome to iDEX ScheduleSpider written by Yi Xie.\nWhere Do you want to save the courses info?")
    Dpath = raw_input()
    Dpath.strip()
    Dpath = Dpath.rstrip("\\")
    isExists = os.path.exists(Dpath)
    if not isExists: # Not Exist
        os.makedirs(Dpath)
        print(Dpath + "\nPath create successful!")
    else:
        print("\nPath exists, Restart...")
        exit(0)
    return Dpath

def write_dicts2csv(dicts,csv_file_path):
    with open(csv_file_path,'wb+') as csv_file:
        headers = dicts[0].keys()
        writer = csv.DictWriter(csv_file,fieldnames = headers)
        writer.writeheader()
        writer.writerows(dicts)

def WriteInCSV(subjectPath, coursesessions, SubjectName, fileCounter):
    dicts = []
    for coursesession in coursesessions:
        time = coursesession[1].split()
        title = coursesession[3].split()
        ct = 1
        coursetitle = ''
        while(ct < len(title)):
            coursetitle += " " + title[ct]
            ct+=1
        if(len(time)< 7):
            dic = {"CRN": coursesession[0],
                   "Time": "TBA",
                   "Day": "TBA",
                   "Course": time[-2] + time[-1],
                   "Location": coursesession[2],
                   "Title": coursetitle
                   }
        else:
            dic = {"CRN": coursesession[0],
                   "Time": time[0]+time[1]+time[2]+time[3][:2],
                   "Day": time[4],
                   "Course": time[-2]+time[-1],
                   "Location": coursesession[2],
                   "Title": coursetitle
                   }
        dicts.append(dic)
    write_dicts2csv(dicts, subjectPath + SubjectName + '.csv')



DataPath = CreatePath()
# Open the web page
browser = webdriver.Chrome()
browser.get('http://classes.ucdavis.edu/')

# TODO: Change Term

# Locate the select tag named subjects  ---- iterate all the subject to get all the course
select = browser.find_element_by_name('subject')

# Regular expression pattern able to get '(Anything)'
pattern = re.compile(r'(\([^\)]*\))')
fields = pattern.findall(select.text)

# Get the all values of select tag
subject = []
for field in fields:
    f= field.encode('utf-8')
    # get rid of wrong data
    if(len(f)<=5):
        # get rid of ()s
        subject.append(f[1:4])
print(subject)


# Use index to choose options from select tag
index = 1
while(index <= len(subject)):
    course = []
    Select(select).select_by_index(index)
    submit = browser.find_element_by_name('search')
    submit.click()
    print("Crawling "+subject[index-1]+"...")
    time.sleep(5)

    # An infinite while loop to wait everything on the page loaded
    ct = 0
    while(index != 0):
        # If we wait for 30sec but no response ---> No search result
        if(ct == 5):
            break
        try:
            # Get the table
            chart = browser.find_element_by_id('mc_win')
            result = ((chart.text).encode('utf-8')).split('\n')
            course = result[8:-4]
        except:
            # keep waiting
            time.sleep(5)
            ct += 1
        else:
            break
    coursesessions = DataOrganizer(course)
    subjectpath = DataPath + '/'
    fileCounter = 0
    try:
        WriteInCSV(subjectpath, coursesessions, subject[index-1], fileCounter)
        print("Finish!")
    except:
        print("No result.")
    fileCounter+=1
    # choose next option
    index+=1

