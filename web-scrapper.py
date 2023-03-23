#!/usr/bin/python3

import pandas, requests, datetime, urllib3, time

from selenium import webdriver 
from selenium.webdriver import Chrome 
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.common.by import By 
from webdriver_manager.chrome import ChromeDriverManager

import sys

from bs4 import BeautifulSoup as bs

# web scrapping code from 
# https://www.zenrows.com/blog/scraping-javascript-rendered-web-pages#installing-the-requirements
# start by defining the options 
options = webdriver.ChromeOptions() 
options.add_argument('--headless') # it's more scalable to work in headless mode 
# normally, selenium waits for all resources to download 
# we don't need it as the page also populated with the running javascript code. 
options.page_load_strategy = 'none' 

# this returns the path web driver downloaded 
chrome_path = ChromeDriverManager().install() 
chrome_service = Service(chrome_path) 
# pass the defined options and service objects to initialize the web driver 
driver = Chrome(options=options, service=chrome_service) 
driver.implicitly_wait(3)

urllib3.disable_warnings()

'''
--------------------------------------------------------------------------------
FUNCTIONS
--------------------------------------------------------------------------------
'''

#Parse Altalink page for toner levels
def get_altalink_levels(ip):
    URL = "http://" + ip + "/stat/welcome.php?tab=status"
    print ("testing URL: " + URL)
    try:
        response = requests.get(URL, verify=False)
    except:
        print("Can't reach " + ip + ", Please check the printer")
        return []
    soup = bs(response.content, "html.parser")
    job_elements = soup.find_all("div", class_="levelIndicatorPercentage")
    levels = []
    for item in job_elements:
        levels.append(float(item.text[1:3]))
    return levels

#Parse the versalink webpage for the toner level
#TODO:Figure out why page is not being fully rendered
def get_versalink_levels(ip):
    URL = "http://" + ip + "/home/index.html#hashHome"
    print ("testing URL: " + URL)
    try:
        driver.get(URL)
        time.sleep(10)
    except:
        print("Can't reach " + ip + ", Please check the printer")
        return []
    content = driver.find_elements(By.CSS_SELECTOR, "li[class*='webui-home-media-text'")
    if (len(content) == 0 ):
        return []
    levels = []
    levels.append(float(content[-1].text.strip("%")))
    return levels

'''
--------------------------------------------------------------------------------
Main Function loop
--------------------------------------------------------------------------------
'''
#Pull in intial file for IPs to scrap
df = pandas.read_csv('test.csv')

#Loop through IPs and get levels. Set the Levels in Pandas and update csv
printer_level_list = []
levels = []
for index, row in df.iterrows():
    if ("AltaLink" in row['Model']):
        levels = get_altalink_levels(row['ip'].strip())
    if ("VersaLink" in row['Model']):
        levels = get_versalink_levels(row['ip'].strip()) 
    printer_level_list.append(levels)

#Testing that the Printers returned levels
print (printer_level_list)
#sys.exit()

i = 0
while i < len(printer_level_list):
    if(len(printer_level_list[i]) == 0):
        print (df.loc[i].at['ip'] + "is unavailable")
        i+=1
        continue
    if(len(printer_level_list[i]) == 1):
       # print("black toner only")#testing only
        df.iat[i,10]= printer_level_list[i][0]
        i+=1
        continue
    #print("color toner")#testing only
    df.iat[i,7]= printer_level_list[i][0]
    df.iat[i,8]= printer_level_list[i][1]
    df.iat[i,9]= printer_level_list[i][2]
    df.iat[i,10]= printer_level_list[i][3]
    i+=1

dt = datetime.datetime.now()
name = "Printer_Levels_" + dt.strftime("%Y-%m-%d") + ".csv"
df.to_csv(name, index=False)