import json
import pprint

import urllib3
import certifi
import bs4
from bs4 import BeautifulSoup
import pandas as pd
import re
from re import search
http = urllib3.PoolManager()

payload = {'covid_resourses_id': '2', 'srch_state_id': '9'}

url = 'https://covidfacts.in/search-form-data'
req = http.request('POST', url, fields=payload)

# print(req.data)
index = 1
soup = BeautifulSoup(req.data, 'lxml')
rows = soup.find('table').find('tbody').find_all('tr')
IDs=[]

rowDict = []

for row in rows:
    if index == 1:
        IDs.append('1')
    else:
        IDs.append(str(index))
    cells = row.find_all("td")
    infoDesc = cells[1].find_all("p")
    hospital = ''
    Description = 'Covid Beds available '
    for info in infoDesc:
        # print(info.get_text())
        if search('No:', info.get_text()):
            phoneNo = info.find("a").get_text()
        else:
            phoneNo = 'NA'
            if search(".com",info.get_text()):
                Description = Description + 'Contact: ' + info.get_text().split(':')[1] + ' '
                print(info.get_text().split(':')[1])
        if search('Organization',info.get_text()):
            hospital = info.get_text()
    if hospital == '':
        if search('Hospital',cells[4].get_text()):
           hospital = cells[4].get_text().strip()
        elif search('Beds', cells[4].get_text()):
            hospital = 'and with Oxygen'
        else:
            hospital = infoDesc[0].get_text()
    Description = Description + hospital + ' '

    # print(cells.find("p").get_text())
    text1 = re.sub(r'[\t\r\n]', '', cells[1].get_text()).strip()
    Description = re.sub(r'[\t\r\n]', '', Description).strip()
    print(Description)
    Category = re.sub(r'[\t\r\n]', '', cells[2].get_text()).strip()
    State = 'Andaman'
    District = re.sub(r'[\t\r\n]', '', cells[3].get_text()).strip()
    rowDict.append({'Description': Description ,'Category' : Category,'State': State,'District':District,'phoneNumber': phoneNo })
    index = index+1
result = dict(zip(IDs, rowDict))

# pprint.pprint(result,sort_dicts=False)

df = pd.DataFrame.from_dict(result, orient="index")
# print(df)

df.to_csv('D:/test.csv')

