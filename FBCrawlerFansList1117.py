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
import json
from threading import Timer
from settings import *


driver = ""
#establish connection to DB
conn = psycopg2.connect(host = Host, database = Database, user = User, password = Password)
#create cursor
cur = conn.cursor()
pageID = ""

def main():

    #driver.set_page_load_timeout(15)
    #throw all page
    print "Start Time: "
    ctime()
    collect = collectMember()
    collect.process()
    time.sleep(15)
    checkThread = Timer(0, checkLag)
    checkThread.start()
    
    print "Collect Done."
    ctime()

    conn.close()
    cur.close()
    driver.close()
    sys.exit(0)

class collectMember():
    
    def __init__(self):
        #set IDset intend to collect
        cur.execute('select fbid from v_page;')
        self.IDset = cur.fetchall()
        conn.commit()
        cur.close()
        
    def process(self):
        global driver
        global conn
        global cur
        
        for eachID in self.IDset:
            #connectDB()
            cur = conn.cursor()
            try:
                cur.execute("select processbit from v_page where fbid = %s",(eachID))
            except:
                print "select processbit error"
                ctime()
                connectDB()
                cur.execute("select processbit from v_page where fbid = %s",(eachID))  
	    global pageID 
	    pageID = eachID[0] 
	    
	    try:
                modValue = float(pageID[len(pageID) - 1: len(pageID)])
            except:
                #print "modValue: " + modValue 
                ctime()
                continue
	    if(modValue % 4 != threadNum):
                print "This ID is not my task."
                continue
            
            try:
                if cur.fetchall()[0][0] == '1':
                    print  pageID + " has been processed."
                    ctime()
                    continue
            except:
                print eachID[0] + "is not in DB"
                ctime()
            cur.close()
            conn.commit()      
            
            #driver = webdriver.Firefox(webdriver.FirefoxProfile(Profile))
            createDriver()
            targetURL = "https://www.facebook.com/search/" + eachID[0] + "/likers?ref=snippets"
            print "Go To "+targetURL
            try:
                driver.get(targetURL)
            except:
                print "Driver crashed, Restart it."
                ctime()
                driver.close()
                cmd = "python "
                cmd += FilePath
                os.system(cmd)
                sys.exit(1)
                
            print ("At Target Page.")
            ctime()
            #Scrolling
            #try:
            self.scrollToBottom()
            #except:
               # ctime()
               # continue
            
            time.sleep(3)
            
            extractPage()
            
  
            print pageID + " processed complete."
            
            cur = conn.cursor()
            try:
                cur.execute("update member set processbit = '1' where name= %s;", (pageID,))
            except:
                ctime()
                connectDB()
                cur.execute("update member set processbit = '1' where name= %s;", (pageID,))
                
            cur.close()
            conn.commit()
            
            ctime()
            print "Close Browser."
            driver.close()
        return 

    def scrollToBottom(self):
        times = 0
        count = 0
	src_updated = driver.page_source
	src = ""
	print "Scrolling ..."
        while 1:
	    src_updated = driver.page_source
	    if src != src_updated:
            	driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
	    	src = src_updated
		times = 0
	    else :
		times += 1
            time.sleep(1)
            count += 1
            if count == 20:
                extractPage()
                count = 0
	    if times == 10:
		break
        return

def createDriver():
    
    global driver
    if Profile == "":
        driver = webdriver.Firefox()
        driver.get("http://facebook.com")
        logButton = WebDriverWait(driver,2).until(EC.visibility_of_element_located((By.ID,"loginbutton")))
        print "Found logButton!"
        driver.find_element_by_id("email").send_keys(FBEmail)
        driver.find_element_by_id("pass").send_keys(FBPass)
        #login click
        logButton.click()

    else:
        driver = webdriver.Firefox(webdriver.FirefoxProfile(Profile))
        
def ctime():
    t = time.time()
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t))
    
def connectDB():
    global conn
    global cur
    print "Connect to DB."
    #establish connection to DB
    conn = psycopg2.connect(host = Host, database = Database, user = User, password = Password)
    #create cursor
    cur = conn.cursor()

def extractPage():
    list = []
    i = 0
    count = 0
    soup = bs(driver.page_source, 'html.parser')
    #使用lxml 將page_source轉成 soup 會有資料大小的上限(部分html會無法存入)
    print "Fetching Data ..."
    for eachContainer in soup("div", id="u_ps_0_3_0")[0]:
        for eachDiv in eachContainer("div", class_="_3u1"):
            try:
                jd = json.loads(eachDiv['data-bt'])
                ID =  jd['id']
            except:
                jd = json.loads(eachDiv.div['data-bt'])
                ID = jd['id']
            count += 1
            name = eachDiv("div", class_="_5d-5")[0].text
            #UnicodeEncodeError: 'ascii' codec can't encode characters in position 0-2: ordinal not in range(128)
            print name.encode('utf-8')
            print ID
            list.append([])
            list[i].append(name)
            list[i].append(ID)
            #i += 1
            #if(i == 100):
            #    time.sleep(1)
            #    i = 0
            #    sendData(list)
            #    list = []
    sendData(list)
    print "Total Member: " 
    print count
    return

def sendData(list):
    global conn
    global cur
    global pageID
    #psycopg2.OperationalError: FATAL:  the database system is in recovery mode
    #connectDB()
    print "Sending Data ..."
    i = 0
    for row in list:
        try:
            name = row[0]
            ID = row[1]
        except:
            #print "List out of range"
            ctime()
            continue
        
        cur = conn.cursor()
        try:
            #execute sql
            cur.execute('select insertfansliker(%s,%s,%s,%s);', (None, pageID, name, str(ID)))
            
        except:
            print "Reconnect to DB."
            ctime()
            connectDB()
            #execute sql
            cur.execute('select insertfansliker(%s,%s,%s,%s);', (None, pageID, name, str(ID)))
        cur.close()
        conn.commit()
        i += 1
        if(i == 100):
            time.sleep(5)
            i = 0

    #conn.close()
    cur.close()
    return

def randomTime(attr):
    if(attr == "long"):
        return random.uniform(2,4)
    if(attr == "short"):
        return random.uniform(0,1)

class timeoutException(Exception):
    def __init__(self, error):
        self.error = error

def checkLag():
    flag = 0
    src_updated = driver.page_source
    src = ""
    while 1:
        #需要有一個等待時間,不然會抓不到driver
        time.sleep(15)
        src_updated = driver.page_source
        try:
            if(src == src_updated):
                print "Current page is equal. Flag= " + flag
                flag+=1
            else:
                src = src_updated
                flag = 0
            if(flag == 3):
                sendData()
                raise timeoutException("restart")
        except Exception as e:
            print e.error
            driver.close()
            cmd = "python "
            cmd += FilePath
            os.system(cmd)
            sys.exit(1)

if __name__ == '__main__':
    main()
