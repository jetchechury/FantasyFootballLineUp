#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import time


# In[2]:


from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from time import sleep


# In[3]:


from bs4 import BeautifulSoup


# In[4]:


# Start Browser
driver = webdriver.Chrome('/usr/local/bin/chromedriver')


# In[5]:


start_time = time.time()

team=[]
salary=[]
# ceil=[]
# floor=[]
point=[]
pt_k=[]
position=[]
category=[]
players=[]


player_type=['qb','rb','wr','te','flex']

page_count=0

# Navigate through qb, rb, wr, te, and flex pages and gather data 
for item in player_type:
    driver.get(f'https://rotogrinders.com/projected-stats/nfl-{item}?site=draftkings')
    sleep(5)
    print(item)
    html=driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    player_panel=soup.find('div',class_='rgt-bdy left')
    player_divs=player_panel.find_all('div',class_='player')
    
    page_count += 1

    players_temp=[]
    
    for item in player_divs:
        player_name=item.find('a',class_='player-popup').text
        players_temp.append(player_name)
        players.append(player_name)

    count=2
    
    for item in players_temp:
        team_scrape=driver.find_element_by_xpath(f'//*[@id="proj-stats"]/div[2]/div[1]/div[2]/div[1]/div[{count}]').text
        position_scrape=driver.find_element_by_xpath(f'//*[@id="proj-stats"]/div[2]/div[1]/div[2]/div[2]/div[{count}]').text
        salaries=driver.find_element_by_xpath(f'//*[@id="proj-stats"]/div[1]/div/div[2]/div[2]/div[{count}]').text

#         ceil_scrape=driver.find_element_by_xpath(f'//*[@id="proj-stats"]/div[3]/div/div[2]/div[1]/div[{count}]').text
#         floor_scrape=driver.find_element_by_xpath(f'//*[@id="proj-stats"]/div[3]/div/div[2]/div[2]/div[{count}]').text
        point_scrape=driver.find_element_by_xpath(f'//*[@id="proj-stats"]/div[3]/div/div[2]/div[3]/div[{count}]').text
        pt_k_scrape=driver.find_element_by_xpath(f'//*[@id="proj-stats"]/div[3]/div/div[2]/div[4]/div[{count}]').text

        salaries1=salaries.strip('$')
        salaries2=salaries1.strip('K')

        
        if page_count < 5:
            category.append(position_scrape)

        else:
            category.append('FLEX')


        position.append(position_scrape)
        team.append(team_scrape)
        salary.append(float(salaries2))
#         ceil.append(float(ceil_scrape))
#         floor.append(float(floor_scrape))
        point.append(float(point_scrape))
        pt_k.append(float(pt_k_scrape))

        count+=1


# In[6]:


# Open Defense Page
driver.get('https://rotogrinders.com/projected-stats/nfl-defense?site=draftkings')
sleep(5)

html=driver.page_source
soup = BeautifulSoup(html, 'html.parser')

player_panel=soup.find('div',class_='rgt-bdy left')
player_divs=player_panel.find_all('div',class_='player')

teams_temp=[]

# Scrape team names
for item in player_divs:
    team_name_scrape=item.find('a',class_='player-popup').text
    players.append(team_name_scrape)
    teams_temp.append(team_name_scrape)


# In[7]:


# Scrape Defense Data

count = 2

for item in teams_temp:
    team_scrape=driver.find_element_by_xpath(f'//*[@id="proj-stats"]/div[2]/div[1]/div[2]/div[1]/div[{count}]').text
    position_scrape=driver.find_element_by_xpath(f'//*[@id="proj-stats"]/div[2]/div[1]/div[2]/div[2]/div[{count}]').text
    
    salaries=driver.find_element_by_xpath(f'//*[@id="proj-stats"]/div[1]/div/div[2]/div[2]/div[{count}]').text

    point_scrape=driver.find_element_by_xpath(f'//*[@id="proj-stats"]/div[3]/div/div[2]/div[1]/div[{count}]').text
    
    pt_k_scrape=driver.find_element_by_xpath(f'//*[@id="proj-stats"]/div[3]/div/div[2]/div[2]/div[{count}]').text

    salaries1=salaries.strip('$')
    salaries2=salaries1.strip('K')
    
    position.append(position_scrape)
    team.append(team_scrape)
    salary.append(float(salaries2))
    point.append(float(point_scrape))
    pt_k.append(float(pt_k_scrape))
    category.append(position_scrape)
    
    count += 1


# In[9]:


stats_df=pd.DataFrame({'Name':players,
                    'Position':position,
                    'Category':category,
                   'Team':team,
                   'Salary($K)':salary,
                    'Proj Points':point,
#                    'Max Points':ceil,
#                     'Min Points':floor,
                    'Pt/$/K':pt_k
                   })


# In[10]:


import pygsheets
import config
from datetime import datetime, date, time, timedelta


# In[11]:


# Connect to google sheets API
gc = pygsheets.authorize(service_file=config.google_api_file_path)


# In[12]:


# Open FF Lineup Stats google sheet
sh = gc.open_by_key(config.sheet_key)


# In[13]:


# Get date time info for worksheet name
now = datetime.now()
today=date.today()
today_full_date=today.strftime('%Y-%m-%d')


# In[14]:


# Create new worksheet to store dataframe info
wks=sh.add_worksheet(today_full_date,rows=1000,cols=6)


# In[15]:


# Load information from dataframe to google sheet
wks.set_dataframe(stats_df,(1,1),index=False,copy_head=True)


# In[ ]:




