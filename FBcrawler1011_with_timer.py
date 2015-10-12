# coding: utf-8


from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import psycopg2
import time
import sys
import random
import threading
import os

#preset Problem
#1. lag when go to the group member page
#2. out of memory

driver = webdriver.Firefox()
def main():
    #navigate to start page

    driver.get("http://facebook.com")

    #setting
    usremail = ""
    usrpass = ""

    #logIn
    logIn(usremail, usrpass)

    #file = open("Log.txt", 'w')

    #wait until load at start page
    while(not isEqualURL("https://www.facebook.com/")):
        time.sleep(randomTime("short"))
        continue
    print "at startup page!"

    time.sleep(randomTime("long"))

    #establish connection to DB
    conn = psycopg2.connect(host = '', database = '', user = '', password = '')
    #create cursor
    cur = conn.cursor()

    #throw all groups
    collectMember(conn, cur);
    print "collect done!"

    conn.close()
    cur.close()
    driver.close()

def collectMember(conn, cur):
    #set groupID intend to collect
    groupID = open("groupID", 'r')
    t = threading.Timer(4.0, checkLag)
    t.start()
    for gID in groupID:
        targetURL = "https://www.facebook.com/browse/group_members/?gid="+ gID + "&edge=groups%3Amembers"
        print "Go To "+targetURL
        driver.get(targetURL)
        print ("at target Page!")

        #scrolling
        scrollToBottom()

        #collect member
        soup = bs(driver.page_source, 'html.parser')
        #groupName=soup("h2", class_="uiHeaderTitle")[0].text
        try:
            groupName = soup.find("h2", class_="uiHeaderTitle").text
            groupName = groupName[11:len(groupName)]
            print groupName
        except:
            print "Grouop not exist!"
            continue

        time.sleep(2)
        #會有名字不見的問題所以重新將soup附值
        soup = bs(driver.page_source, 'html.parser')
        #使用lxml 將page_source轉成 soup 會有資料大小的上限(部分html會無法存入)

        for eachDiv in soup("div", class_="fsl fwb fcb"):
            try:
                name = eachDiv.a.text
                ID = splitID(eachDiv.a['data-hovercard'])
                #execute sql
                #cur.execute('select "InsertFBMember(%s,%s,%s)";', (groupName, name, ID))
                cur.callproc('"InsertFBMember"', [groupName, name, ID])

                #commit data
                conn.commit()
                print name + " " + ID
            except:
                print 'sql connect problem'
                #reconnect to DB
                conn = psycopg2.connect(host = '10.10.59.117', database = 'FBGroup-i3s', user = 'carr', password = 'ssss6302')
                #create cursor
                cur = conn.cursor()
                time.sleep(1)
                cur.callproc('"InsertFBMember"', [groupName, name, ID])
                #commit data
                conn.commit()
                print name + " " + ID
                continue

def checkLag():
	flag = 0
	try:
		while(driver.find_element_by_class_name('fbxWelcomeBoxName')):
			time.sleep(2)
			flag += 1
			if(flag == 3):
	 			os.system('python FBCrawler_timer_test.py')
				driver.close()
	except:
		return	
def splitID(attribute):
    index = attribute.find("id=")
    index += 3
    ID = ""
    while(attribute[index].isdigit()):
        ID += attribute[index]
        index += 1
    return ID

def scrollToBottom():
    #scroll times
    times = 1
    #count timeOut
    timeOut = 0
    while(times > 0):
        #test use
        #times -=1
        time.sleep(randomTime("long"))
        print "scroll"
        try:
            #find the "see more " bottom
            driver.find_element_by_xpath("//div[@id='u_0_1']//div[@class='clearfix mam uiMorePager stat_elem morePager _52jv']")
        except :
            #print "Unexpected error:", sys.exc_info()[0]
            #print "doesn't found anymore"
            timeOut += 1
            if(timeOut > 2):
                print "timeOut"
                return
            continue
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    return

def isEqualURL(URL):
    return driver.current_url == URL

def logIn(usremail, usrpass):
    logButton = WebDriverWait(driver,2).until(EC.visibility_of_element_located((By.ID,"loginbutton")))
    print "found logButton!"
    driver.find_element_by_id("email").send_keys(usremail)
    driver.find_element_by_id("pass").send_keys(usrpass)
    #login click
    logButton.click()
    return

def randomTime(attr):
    if(attr == "long"):
        return random.uniform(2,4)
    if(attr == "short"):
        return random.uniform(0,1)

if __name__ == '__main__':
    main()
