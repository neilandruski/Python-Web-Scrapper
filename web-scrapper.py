#!/usr/bin/python3

import pandas, requests
from bs4 import BeautifulSoup as bs

#Scraps page for toner levels and returns array of levels
#TODO: work on return array
def get_levels(ip):
    URL = "http://" + ip + "/stat/welcome.php?tab=status"
    print (URL)
    response = requests.get(URL, verify=False)
    soup = bs(response.content, "html.parser")
    job_elements = soup.find_all("div", class_="levelIndicatorPercentage")
    print(job_elements)


#Pull in intial file for IPs to scrap
df = pandas.read_csv('test.csv')

'''
#test printing and learning Pandas to parse csvs
print (df)

for column in df.columns[5:]:
    print(df[column])

#Figured out how to get the javascript to render by going to full site address not just IP
URL = "http://" + df["ip"][1] + "/stat/welcome.php?tab=status"
print(URL)
'''

#Loop through IPs and get levels. Set the Levels in Pandas and update csv
#TODO: get array and update the csv
for ip in df["ip"]:
    print(ip)
    levels = get_levels(ip)



'''
#Testing bs and retrieving the correct location of levels from HTML
response = requests.get(URL, verify=False)
soup = bs(response.content, "html.parser")

#print(soup)
job_elements = soup.find_all("div", class_="levelIndicatorPercentage")

print(job_elements)
'''   