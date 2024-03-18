# -*- coding: utf-8 -*-
"""
Created on Wed Oct 12 13:49:09 2022

@author: Govind.Kumar
"""


import time
import pandas as pd
from argparse import ArgumentParser
import argparse
import logging
import logging.config
from selenium import webdriver as wd
from selenium.webdriver import ActionChains
import selenium
import numpy as np
#from schema import SCHEMA
import json
import urllib
import datetime as dt

#imports here
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
import time

start = time.time()

DEFAULT_URL = ('https://www.glassdoor.co.in/Interview/Fractal-Interview-Questions-E270403.htm')

parser = ArgumentParser()
parser.add_argument('-u', '--url',
                    help='URL of the company\'s Glassdoor landing page.',
                    default=DEFAULT_URL)
parser.add_argument('-f', '--file', default='glassdoor_ratings.csv',
                    help='Output file.')
parser.add_argument('--headless', action='store_true',
                    help='Run Chrome in headless mode.')
parser.add_argument('--username', help='Email address used to sign in to GD.')
parser.add_argument('-p', '--password', help='Password to sign in to GD.')
parser.add_argument('-c', '--credentials', help='Credentials file')
parser.add_argument('-l', '--limit', default=25,
                    action='store', type=int, help='Max reviews to scrape')
parser.add_argument('--start_from_url', action='store_true',
                    help='Start scraping from the passed URL.')
parser.add_argument(
    '--max_date', help='Latest review date to scrape.\
    Only use this option with --start_from_url.\
    You also must have sorted Glassdoor reviews ASCENDING by date.',
    type=lambda s: dt.datetime.strptime(s, "%Y-%m-%d"))
parser.add_argument(
    '--min_date', help='Earliest review date to scrape.\
    Only use this option with --start_from_url.\
    You also must have sorted Glassdoor reviews DESCENDING by date.',
    type=lambda s: dt.datetime.strptime(s, "%Y-%m-%d"))
args = parser.parse_args()

if not args.start_from_url and (args.max_date or args.min_date):
    raise Exception(
        'Invalid argument combination:\
        No starting url passed, but max/min date specified.'
    )
elif args.max_date and args.min_date:
    raise Exception(
        'Invalid argument combination:\
        Both min_date and max_date specified.'
    )

if args.credentials:
    with open(args.credentials) as f:
        d = json.loads(f.read())
        args.username = d['username']
        args.password = d['password']
else:
    try:
        with open('secret.json') as f:
            d = json.loads(f.read())
            args.username = d['username']
            args.password = d['password']
    except FileNotFoundError:
        msg = 'Please provide Glassdoor credentials.\
        Credentials can be provided as a secret.json file in the working\
        directory, or passed at the command line using the --username and\
        --password flags.'
        raise Exception(msg)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)
formatter = logging.Formatter(
    '%(asctime)s %(levelname)s %(lineno)d\
    :%(filename)s(%(process)d) - %(message)s')
ch.setFormatter(formatter)

logging.getLogger('selenium').setLevel(logging.CRITICAL)
logging.getLogger('selenium').setLevel(logging.CRITICAL)


def more_pages():
    try:
        current = browser.find_element(By.CLASS_NAME,'selected')
        pages = browser.find_element(By.CLASS_NAME,'pageContainer').text.split()
        if int(pages[-1]) != int(current.text):
            return True
        else:
            return False
    except selenium.common.exceptions.NoSuchElementException:
        return False


def go_to_next_page():
    logger.info(f'Going to page {page[0] + 1}')
    next_ = browser.find_element(By.CLASS_NAME,'nextButton')
    ActionChains(browser).click(next_).perform()
    time.sleep(5) # wait for ads to load
    page[0] = page[0] + 1


def go_to_prev_page():
    logger.info(f'Going to page {page[0] - 1}')
    next_ = browser.find_element(By.CLASS_NAME,'prevButton')
    ActionChains(browser).click(next_).perform()
    time.sleep(3) # wait for ads to load
    page[0] = page[0] - 1


    


def get_browser():
    logger.info('Configuring browser')
    chrome_options = wd.ChromeOptions()
    if args.headless:
        chrome_options.add_argument('--headless')
    chrome_options.add_argument('log-level=3')
    browser = wd.Chrome(options=chrome_options)
    return browser


def get_current_page():
    logger.info('Getting current page number')
    current = browser.find_element(By.CLASS_NAME,'selected')
    return int(current.text)    
    
def sign_in():
    logger.info(f'Signing in to {args.username}')

    url = 'https://www.glassdoor.co.in/profile/login_input.htm'

    browser.get(url)
    browser.maximize_window()

    try:       
        email_field = browser.find_element('id', 'inlineUserEmail')
        password_field = browser.find_element('id','inlineUserPassword')
        #submit_btn = browser.find_element_by_xpath('//button[@type="submit"]')
    
        email_field.send_keys(args.username)
        password_field.send_keys(args.password)
        submit_btn = browser.find_element(By.CLASS_NAME,'emailButton')
        submit_btn.click()
    except:
        email_field = browser.find_element('id', 'inlineUserEmail')
        email_field.send_keys(args.username)
        conti_email = browser.find_element(By.CLASS_NAME,'emailButton')
        conti_email.click()
        time.sleep(3)
        try:            
            password_field = browser.find_element('id','inlineUserPassword')
        except:
            password_field = browser.find_element('id','inlineUserPassword')
            
        password_field.send_keys(args.password)
        submit_btn = browser.find_element(By.CLASS_NAME,'emailButton')
        submit_btn.click()

    time.sleep(3)
    browser.get(args.url)
    
    
def helpful_count(a):          
    if "Be" in a[-4]:               
        temp = 0
    else:
        temp = a[-4].split(' ')[0]         
    return int(temp)

def get_application(a):
    i=0
    for i in range(len(a)):
        if a[i] == 'Application':
            b = a[i+1]
            break
        else:
            b = 'null'
    return b

def get_feedback(a):
    i=0
    for i in range(len(a)):
        if a[i] == 'Interview':
            b = a[i+1]
            break
        else:
            b = 'null'
    return b

def get_questions(a):
    i=0
    for i in range(len(a)):
        if a[i] == 'Interview Questions':
            b = a[i+1]
            break
        else:
            b = 'null'
    return b

def get_offer_status(review):
    b = (review.find_elements(By.CLASS_NAME,'mb-xxsm'))
    i=0
    for i in range(2,len(b)):
        try:
            c = b[i].text.split("\n")[0]
            if 'Offer' in c:
                d = c
            else:
                d = 'null'
        except:
            d = 'null'
        if d == c:
            break
    return d

def get_difficulty_level(review):
    b = (review.find_elements(By.CLASS_NAME,'mb-xxsm'))
    i=0
    for i in range(2,len(b)):
        try:
            c = b[i].text.split("\n")[0]
            if 'Interview' in c:
                d = c
            else:
                d = 'null'
        except:
            d = 'null'
        if d == c:
            break
    return d

def get_interview_exp(review):
    b = (review.find_elements(By.CLASS_NAME,'mb-xxsm'))
    i=0
    for i in range(2,len(b)):
        try:
            c = b[i].text.split("\n")[0]
            if 'Experience' in c:
                d = c
            else:
                d = 'null'
        except:
            d = 'null'
        if d == c:
            break
    return d

def extract_reviews():    
    reviews = browser.find_elements(By.CLASS_NAME,'css-cup1a5')
    df = pd.DataFrame()
    for review in reviews:
        a = review.text.split("\n")
        dic = {'Date':a[0],
               'Interviewed_role':a[1],
               'Employee_status':a[2],
               'Offer_status':get_offer_status(review),
               'Interview_exp':get_interview_exp(review), 
               'Difficulty_level':get_difficulty_level(review),
               'Application':get_application(a),
               'Feedback':get_feedback(a),
               'Questions':get_questions(a),
               'helpful Count':helpful_count(a)}
        df = df.append(dic,ignore_index=True)
    return df



browser = get_browser()
page = [1]
idx = [0]
sign_in()
res_df = extract_reviews()

while more_pages(): 
    go_to_next_page()       
    browser.refresh()
    time.sleep(2)
    try:
        temp = extract_reviews()
        res_df = res_df.append(temp)
    except:
        break


res_df.to_excel(r'Fractal_glassdoor_interviews.xlsx', index=False)


