"""
Created on Fri Jul 26 15:53:20 2019

@author: Gerard Mazi
@email: gerard.mazi@gmail.com
@phone: 862.221.2477
"""


import pandas as pd
import numpy as np
from selenium import webdriver
import time
from datetime import date

dep = pd.read_pickle('dep.pkl')

hsb_date = date.today()

chrome_path = r"chromedriver.exe"
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
    
    apy = driver.find_elements_by_xpath('//div[@class = "apy"]/span')
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

# Load Deposit Rates and append new data
dep = pd.concat([dep, nu_rates], ignore_index = True)

# Add up to date HSB deposit data
hsb_rates = [('HomeStreet Bank', '3 month cd',  0.40, '', hsb_date, '03 Month'),
             ('HomeStreet Bank', '7 month cd',  1.70, '', hsb_date, '06 Month'),
             ('HomeStreet Bank', '11 month cd', 1.80, '', hsb_date, '12 Month'),
             ('HomeStreet Bank', '13 month cd', 1.90, '', hsb_date, '12 Month'),
             ('HomeStreet Bank', '15 month cd', 1.95, '', hsb_date, '12 Month'),
             ('HomeStreet Bank', '18 month cd', 2.00, '', hsb_date, '18 Month'),
             ('HomeStreet Bank', '22 month cd', 2.05, '', hsb_date, '24 Month'),
             ('HomeStreet Bank', '36 month cd', 2.10, '', hsb_date, '36 Month'),
             ('HomeStreet Bank', '48 month cd', 0.00, '', hsb_date, '48 Month'),
             ('HomeStreet Bank', '60 month cd', 2.10, '', hsb_date, '60 Month'),
             ('HomeStreet Bank', 'Savings',     0.20, '', hsb_date, 'Savings' ),
             ('HomeStreet Bank', 'PPMMS',       2.25, '', hsb_date, 'Money Market')]
hsb_data = pd.DataFrame(hsb_rates, columns = list(dep))

# Append and save
dep = pd.concat([dep, hsb_data], ignore_index = True)
dep.to_pickle('dep.pkl')

#######################################################################################################################
# ANALYTICS AND TRENDS

hsb_trend = dep[dep.Bank=='HomeStreet Bank'].groupby(['Date','Product'])['Rate'].mean().unstack()
hsb_trend.plot()

means = dep.groupby(['Date','Product']).mean().unstack()
means.plot()

median = dep.groupby(['Date','Product']).median().unstack()
median.plot()

quantile = dep.groupby(['Date','Product']).quantile(0.99).unstack()
quantile.plot()

max_rate = dep.groupby(['Date','Product'])['Rate'].max().unstack()
max_rate.plot()

#################################################################################################################
# COMPETITOR ANALYTICS

# Peer Comps (Peer banks based on assets, footprint, and direct competition for deposits)
peers = ['Banner Bank','Columbia State Bank','Washington Federal','Luther Burbank Savings','Umpqua Bank',
         'First Financial Northwest Bank','Bank of California','BECU (Boeing Employees Credit Union)',
         'Bank of the West','Union Bank (San Francisco, CA)','Seattle Bank','Opus Bank','KeyBank','US Bank',
         'Cashmere Valley Bank','Gesa Credit Union','Mountain Pacific Bank','HomeStreet Bank',
         'Seattle Credit Union']
peer_mean = dep[dep.Bank.isin(peers)].groupby(['Date', 'Product']).mean().unstack()
peer_mean.plot()
peer_rates = dep.loc[(dep.Bank.isin(peers)) & (dep.Date == hsb_date), ['Bank','Product','Rate']]
peer_comps = pd.crosstab(
    peer_rates.Bank,
    peer_rates.Product,
    values=peer_rates.Rate,
    aggfunc=np.mean
)

# Online Comps (Banks with a 100% online business model)
online = ['Capital One','Goldman Sachs Bank USA','Synchrony Bank','Ally Bank','TIAA Bank','Discover Bank',
           'American Express National Bank','CIT Bank','Barclays','HomeStreet Bank','WebBank','MemoryBank']
online_mean = dep[dep.Bank.isin(online)].groupby(['Date', 'Product']).mean().unstack()
online_mean.plot()
online_rates = dep.loc[(dep.Bank.isin(online)) & (dep.Date == hsb_date), ['Bank','Product','Rate']]
online_comps = pd.crosstab(
    online_rates.Bank,
    online_rates.Product,
    values=online_rates.Rate,
    aggfunc=np.mean
)

# Large Comps (Large money centers)
large = ['Bank of America','Chase Bank','Wells Fargo Bank','Citi','HomeStreet Bank']
large_mean = dep[dep.Bank.isin(large)].groupby(['Date', 'Product']).mean().unstack()
large_mean.plot()
large_rates = dep.loc[(dep.Bank.isin(large)) & (dep.Date == hsb_date), ['Bank','Product','Rate']]
large_comps = pd.crosstab(
    large_rates.Bank,
    large_rates.Product,
    values=large_rates.Rate,
    aggfunc=np.mean
)

# Digital Comps (Branch banks with an established digital strategy)
digital = ['PNC Bank','KeyBank','BBVA','HomeStreet Bank','Investors eAccess','Northpointe Bank',
           'iGObanking','BankUnitedDirect','Zions Bank','Banesco USA','MySavingsDirect','Salem Five Direct',
           'Rising Bank','Citizens Access','Vio Bank','HSBC Direct']
digital_mean = dep[dep.Bank.isin(digital)].groupby(['Date', 'Product']).mean().unstack()
digital_mean.plot()
digital_rates = dep.loc[(dep.Bank.isin(digital)) & (dep.Date == hsb_date), ['Bank','Product','Rate']]
digital_comps = pd.crosstab(
    digital_rates.Bank,
    digital_rates.Product,
    values=digital_rates.Rate,
    aggfunc=np.mean
)

# Startup comps
startup = ['PNC Bank','BBVA','Investors eAccess','MySavingsDirect','Salem Five Direct','HSBC Direct','TAB Bank',
           'Comenity Direct','Barclays','Goldman Sachs Bank USA','MemoryBank','American Express National Bank',
           'Capital One','Live Oak Bank']
startup_mean = dep[dep.Bank.isin(startup)].groupby(['Date', 'Product']).mean().unstack()
startup_mean.plot()
startup_rates = dep.loc[(dep.Bank.isin(startup)) & (dep.Date == hsb_date), ['Bank','Product','Rate']]
startup_comps = pd.crosstab(
    startup_rates.Bank,
    startup_rates.Product,
    values=startup_rates.Rate,
    aggfunc=np.mean
)
