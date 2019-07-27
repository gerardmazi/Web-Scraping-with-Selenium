# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 15:53:20 2019

@author: gmazi
"""


import pandas as pd
from selenium import webdriver
import time
from datetime import date
import matplotlib.pyplot as plt

chrome_path = r"K:/Treasury/CORPORATE TREASURY/Weekly Retail Pricing Package/Deposit Analytics/Deposit Rates/chromedriver.exe"
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
nu_rates = nu_rates[nu_rates.Bank != 'HomeStreet Bank']

# Load Deposit Rates and apend new data
dep = pd.read_pickle('K:/Treasury/CORPORATE TREASURY/Weekly Retail Pricing Package/Deposit Analytics/Deposit Rates/dep.pkl')
dep = pd.concat([dep, nu_rates], ignore_index = True)

# Add up to date HSB deposit data
hsb_date = date(2019, 7, 23)
hsb_rates = [('HomeStreet Bank', '3 month cd',  0.40, '', hsb_date, '03 Month'),
             ('HomeStreet Bank', '7 month cd',  2.00, '', hsb_date, '06 Month'),
             ('HomeStreet Bank', '11 month cd', 2.10, '', hsb_date, '12 Month'),
             ('HomeStreet Bank', '13 month cd', 2.20, '', hsb_date, '12 Month'),
             ('HomeStreet Bank', '15 month cd', 2.25, '', hsb_date, '12 Month'),
             ('HomeStreet Bank', '18 month cd', 2.30, '', hsb_date, '18 Month'),
             ('HomeStreet Bank', '22 month cd', 2.35, '', hsb_date, '24 Month'),
             ('HomeStreet Bank', '36 month cd', 2.40, '', hsb_date, '36 Month'),
             ('HomeStreet Bank', '60 month cd', 2.40, '', hsb_date, '60 Month'),
             ('HomeStreet Bank', 'Savings',     0.20, '', hsb_date, 'Savings' ),
             ('HomeStreet Bank', 'PPMMS',       2.25, '', hsb_date, 'Money Market')]
hsb_data = pd.DataFrame(hsb_rates, columns = list(dep))

# Append and save
dep = pd.concat([dep, hsb_data], ignore_index = True)
dep.to_pickle('K:/Treasury/CORPORATE TREASURY/Weekly Retail Pricing Package/Deposit Analytics/Deposit Rates/dep.pkl')

#########################################################################################
# ANALYTICS AND TRENDS

hsb_trend = dep[dep.Bank=='HomeStreet Bank'].groupby(['Date','Product'])['Rate'].mean().unstack()

means = dep.groupby(['Date','Product']).mean().unstack()
means.plot()

median = dep.groupby(['Date','Product']).median().unstack()
median.plot()

quantile = dep.groupby(['Date','Product']).quantile(0.99).unstack()
quantile.plot()

max_rate = dep.groupby(['Date','Product'])['Rate'].max().unstack()
max_rate.plot()
