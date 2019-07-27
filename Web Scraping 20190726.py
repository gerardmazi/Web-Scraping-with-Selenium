"""
Created on Fri Jul 26 15:53:20 2019

@author: Gerard Mazi
@email: gerard.mazi@gmail.com
@phone: 862.221.2477
"""


import pandas as pd
from selenium import webdriver
import time
from datetime import date
import matplotlib.pyplot as plt

# Download and extract chromedriver.exe from http://chromedriver.chromium.org/downloads
chrome_path = r"C:/.../chromedriver.exe"
driver = webdriver.Chrome(chrome_path)

url = ['https://www.depositaccounts.com/cd/3-month-cd-rates.html',
       'https://www.depositaccounts.com/cd/6-month-cd-rates.html',
       'https://www.depositaccounts.com/cd/',
       'https://www.depositaccounts.com/cd/18-month-cd-rates.html',
       'https://www.depositaccounts.com/cd/2-year-cd-rates.html',
       'https://www.depositaccounts.com/cd/3-year-cd-rates.html',
       'https://www.depositaccounts.com/cd/4-year-cd-rates.html',
       'https://www.depositaccounts.com/cd/5-year-cd-rates.html',
       'https://www.depositaccounts.com/savings/',
       'https://www.depositaccounts.com/moneymarket/']

# Flag for deposit product or CD term if Cd
product = ['03 Month', '06 Month', '12 Month','18 Month','24 Month',
           '36 Month','48 Month', '60 Month','Savings','Money Market']

# Merge URL's and Products
lookup = pd.DataFrame({"URL":url, "Product":product})

# Create empty DataFrame to be filled in by loop
nu_rates = pd.DataFrame({"Bank":[], "Product_Name":[], "Rate":[], "URL":[]})

# Scrape
for u in lookup['URL'].tolist():
    driver.get(u)
    driver.find_element_by_xpath('//*[@id="rtShowMore"]').click()
    time.sleep(8)
    
    bank, prod, rates = [],[],[]
    
    banks = driver.find_elements_by_class_name('name')
    for b in banks:
        bank.append(b.text)
            
    prod_nam = driver.find_elements_by_xpath('//div[@class = "bank"]/span')
    for p in prod_nam:
        prod.append(p.text)
    
    apy = driver.find_elements_by_class_name('apy')
    for a in apy:
        rates.append(a.text)
    
    url = u
    
    temp = pd.DataFrame({"Bank":bank, "Product_Name":prod, "Rate":rates, "URL": url})
    
    nu_rates = pd.concat([nu_rates, temp], ignore_index = True)

# Cleanup: Add Date, Add Product Type, Coerce rate to float, remove HSB data    
nu_rates["Date"] = date.today()
nu_rates = pd.merge(nu_rates, lookup, on='URL',how='left')
nu_rates['Rate'] = nu_rates['Rate'].str[:4].astype('float')

# Load a running file to which you append new data
