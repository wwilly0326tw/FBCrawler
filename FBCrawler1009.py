
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

#preset Problem
#1. lag when go to the group member page
#2. out of memory 

driver = webdriver.Firefox()

def main():
    #navigate to start page
    
    driver.get("http://facebook.com")
    
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
    #throw all groups 
    collectMember();
    print "collect done!"
    
    driver.close()
    
def collectMember():
    #set groupID intend to collect
    groupID = open("groupID", 'r')

    for gID in groupID:
        print "go to"+ "https://www.facebook.com/browse/group_members/?gid="+ gID + "&edge=groups%3Amembers"
	targetURL = "https://www.facebook.com/browse/group_members/?gid="+ gID + "&edge=groups%3Amembers"
        driver.get(targetURL)
        
#        while(not isEqualURL(targetURL)):
#            time.sleep(3)
#            print "too slow!"
#            driver.get(targetURL)
            
        print ("at target Page!")
        
        #scrolling
        scrollToBottom()
        
        #collect member
        soup = bs(driver.page_source, 'lxml')
        for eachDiv in soup("div", class_="fsl fwb fcb"):
            try:
                name = eachDiv.a.text
                ID = splitID(eachDiv.a['data-hovercard'])
                print name + " " + ID
            except:
                print 'codec problem'
                continue
            #file.write(text)
            
def splitID(attribute):
    index = attribute.find("id=")
    index += 3
    ID = ""
    while(attribute[index].isdigit()):
        ID += attribute[index]
        index += 1
    return ID

def scrollToBottom():
    # f = open("source.txt",'w')
    # f.write(driver.page_source.encode('UTF-8'))
    # f.close()
    #driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    times = 5
    timeOut = 0
    while(times > 0):
        times -=1
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
    #driver.find_element_by_id("u_0_v").click()
    logButton.click()
    return

def randomTime(attr):
    if(attr == "long"):
        return random.uniform(3,5)
    if(attr == "short"):
        return random.uniform(1,2)
    
if __name__ == '__main__':
    main()

