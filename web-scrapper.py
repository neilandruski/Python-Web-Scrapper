#!~/opt/anaconda3/bin/python3

import pandas, requests, datetime, urllib3, time
from bs4 import BeautifulSoup as bs

from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.webdriver.chrome.service import Service

service = Service()
options = webdriver.ChromeOptions()
options.add_argument('--headless') # it's more scalable to work in headless mode 
driver = webdriver.Chrome(service=service, options=options)
driver.implicitly_wait(3)

#Ignore http warning and go to site
urllib3.disable_warnings()

'''
--------------------------------------------------------------------------------
FUNCTIONS
--------------------------------------------------------------------------------
'''

def get_altalink_levels(ip: str) -> [str]: # type: ignore
    """
    get the toner levels for altalink models

    :param ip: string version of an ip
    :return: array of strings for the current levels
    """

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
        levels.append(float(item.text.strip("\n%")))
    return levels


def get_versalink_levels(ip: str) -> [str]: # type: ignore
    """
    get the toner levels for Versalink models

    :param ip: string version of an ip
    :return: array of strings for the current levels
    """

    URL = "http://" + ip + "/home/index.html#hashHome"
    print ("testing URL: " + URL)
    try:
        driver.get(URL)
        time.sleep(5)
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

#Loop through IP list in Pandas. Set the Levels in new Array
printer_level_list = []
levels = []
for index, row in df.iterrows():
    if ("AltaLink" in row['Model']):
        levels = get_altalink_levels(row['ip'].strip())
    if ("VersaLink" in row['Model']):
        levels = get_versalink_levels(row['ip'].strip()) 
    printer_level_list.append(levels)

#Loop through Levels Array and update Pandas.
i = 0
while i < len(printer_level_list):
    if(len(printer_level_list[i]) == 0):
        #print (df.loc[i].at['ip'] + "is unavailable")
        i+=1
        continue
    if(len(printer_level_list[i]) == 1):
        #print("black toner only")#testing only
        df.iat[i,10]= printer_level_list[i][0]
        i+=1
        continue
    #print("color toner")#testing only
    df.iat[i,7]= printer_level_list[i][0]
    df.iat[i,8]= printer_level_list[i][1]
    df.iat[i,9]= printer_level_list[i][2]
    df.iat[i,10]= printer_level_list[i][3]
    i+=1

#Get current date and save Pandas to new csv
dt = datetime.datetime.now()
name = "Levels/Printer_Levels_" + dt.strftime("%Y-%m-%d") + ".csv"
df.to_csv(name, index=False)

driver.quit()