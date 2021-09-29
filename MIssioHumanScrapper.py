import pprint
import time
import pandas as pd
import requests
import urllib3
import re
from re import search
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

http = urllib3.PoolManager()
options = webdriver.ChromeOptions()
# options.add_argument("user-agent=Chrome/87.0.4280.88")
# options.add_argument('headless')
options.add_argument('--window-size=1920,1080')
driver = webdriver.Chrome(executable_path="D:\Drivers\chromedriver.exe", options=options)
URL = "https://www.covidfacts.in/"
driver.get(URL)

r = requests.get(URL)
# print(r.content)
start_time = time.time()
soup = BeautifulSoup(r.content, 'html5lib') # If this line causes an error, run 'pip install html5lib' or install html5lib

# print(soup.prettify())
# check for popup
isAvailable = len(driver.find_elements_by_xpath("//*[@id='browserinfo']/div/div"))
if isAvailable > 0:
    if driver.find_element_by_xpath("//*[@id='browserinfo']/div/div").is_displayed():
        driver.find_element_by_xpath("//*[@id='browserinfobtn']").click()

resources = soup.find('select',attrs = {'name':'covid_resourses_id'}).findAll('option')
tab = driver.find_element_by_class_name('content-wrapper')
form = tab.find_element_by_class_name('box-body')
resource = Select(form.find_element_by_name('covid_resourses_id'))
stateID = Select(form.find_element_by_name('srch_state_id'))
for option in resources:
    if option.text == 'Covid Beds':
        resource.select_by_visible_text(option.text)
        states = soup.find('select',attrs={'name':'srch_state_id'}).findAll('option')
        index = 1
        IDs = []
        rowDict = []
        for state in states:
            bNoRecord = False
            if state.text != 'Select':
                stateID.select_by_visible_text(state.text)
                button = form.find_element_by_xpath('//*[@id="searchform"]/div/div[2]/div/button')
                button.click()
                WebDriverWait(driver, 50).until(ec.presence_of_element_located((By.ID, 'ajaxsearchreslt')))
                # time.sleep(2)
                searchResults = tab.find_element_by_id('ajaxsearchreslt')
                print('Progress for state: ' + state.text)
                rID = option['value']
                sID = state['value']
                http = urllib3.PoolManager()
                payload = {'covid_resourses_id': rID, 'srch_state_id': sID}

                url = 'https://covidfacts.in/search-form-data'
                req = http.request('POST', url, fields=payload)

                # time.sleep(2)
                WebDriverWait(driver, 50).until(ec.presence_of_element_located((By.CLASS_NAME, 'panel')))
                soup = BeautifulSoup(req.data, 'lxml')
                rows = soup.find('table').find('tbody').find_all('tr')


                for row in rows:
                    if row.get_text() == 'No Records..!!':
                        bNoRecord = True
                        continue
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
                            phoneNo = info.get_text().split(':')[1]
                        else:
                            phoneNo = 'NA'
                            if search(".com", info.get_text()):
                                Description = Description + 'Contact: ' + info.get_text().split(':')[1] + ' '
                                # print(info.get_text().split(':')[1])
                        if search('Organization', info.get_text()):
                            hospital = info.get_text()
                    if hospital == '':
                        if search('Hospital', cells[4].get_text()):
                            hospital = cells[4].get_text().strip()
                        elif search('Beds', cells[4].get_text()):
                            hospital = 'and with Oxygen'
                        else:
                            hospital = infoDesc[0].get_text()
                    Description = Description + hospital + ' '

                    # print(cells.find("p").get_text())
                    text1 = re.sub(r'[\t\r\n]', '', cells[1].get_text()).strip()
                    Description = re.sub(r'[\t\r\n]', '', Description).strip()
                    #print(Description)
                    Category = re.sub(r'[\t\r\n]', '', cells[2].get_text()).strip()
                    State = state.text
                    District = re.sub(r'[\t\r\n]', '', cells[3].get_text()).strip()
                    phoneNo = re.sub(r'[\t\r\n]', '', phoneNo).strip()
                    rowDict.append(
                        {'Description': Description, 'Category': Category, 'State': State, 'District': District,
                         'phoneNumber': phoneNo})
                    index = index + 1

                result = dict(zip(IDs, rowDict))

print("--- %s seconds ---" % (time.time() - start_time))
pprint.pprint(result, sort_dicts=False)
results_df = pd.DataFrame.from_dict(result, orient="index")

results_df.to_csv('D:/test.csv')