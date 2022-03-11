# -*- coding: utf-8 -*-
"""
@author: Steven Marin
Simple web crawler. Scrapes data for several categories present in
https://www.imdb.com/ and stores it as excel file .xlsx
"""

from selenium import webdriver
import pandas as pd
import time


""" Main function that scrapes the imdb website and saves data as .xlsx file """
def scrapeIMDB():
    """ Creating firefox driver and getting to imdb website."""
    home_url = 'https://www.imdb.com/'
    driver = webdriver.Firefox()
    driver.get(home_url)
    
    """ Getting sections of interest and process each section"""
    df_sections = getSections(driver)
    for index, row in df_sections.iterrows(): 
        time.sleep(1)
        driver.get(row['url'])
        if  row['section_name'] == 'Fan favorites':
            df_fan_favorites = scrapeFanFavorites(driver)
        elif row['section_name'] == 'In theaters':
            df_in_theaters = scrapeInTheaters(driver)
        elif row['section_name'] == 'Top box office (US)':
            df_box_office = scrapeTopBoxOffice(driver)
        elif row['section_name'] == 'Coming soon to theaters (US)':
            df_coming_soon = scrapeComingSoon(driver)
        else:
            continue
            
    """ Writing the final excel spreadsheet with one tab per section"""
    with pd.ExcelWriter('scraped_data.xlsx') as writer:  
        df_fan_favorites.to_excel(writer, sheet_name='Fan favorites', index = False)
        df_in_theaters.to_excel(writer, sheet_name='In theaters', index = False)
        df_box_office.to_excel(writer, sheet_name='Top box office (US)', index = False)
        df_coming_soon.to_excel(writer, sheet_name='Coming soon to theaters (US)', index = False)


""" Function to find and store each section and its url"""
def getSections(driver):
    xpath = """.//div//a//h3[@class='ipc-title__text']//parent::a"""
    movie_sections =  driver.find_elements('xpath', xpath)
    movie_sections_list = []
    for section in movie_sections:
        section_name = section.text.split('\n')[0]
        url = section.get_attribute('href')
        section_dict = {'section_name':section_name, 'url':url}
        movie_sections_list.append(section_dict)
    df_sections = pd.DataFrame(movie_sections_list)
    sections_to_ignore = ['From your Watchlist', 'Born today', 'Top news']
    df_sections = df_sections[~df_sections['section_name'].isin(sections_to_ignore)]
    return df_sections    

""" Function that scrapes Fan Favorites section """
def scrapeFanFavorites(driver):
    movies = driver.find_elements('xpath',""".//span[@data-testid='title']""")
    movie_list = []
    for movie in movies:
        movie_name = movie.text
        movie_rating = movie.find_element('xpath', """ .//parent::a//parent::div//span[contains(@class,'ipc-rating-star')]""").text
        movie_url = movie.find_element('xpath', """ .//parent::a """).get_attribute('href')
        movie_list.append({'Name':movie_name, 'Rating':movie_rating, 'URL':movie_url})
    df_fan_favorites = pd.DataFrame(movie_list)
    return df_fan_favorites

""" Function that scrapes In Theaters section"""
def scrapeInTheaters(driver):
    movie_tab = driver.find_element('xpath', """.//div[@id='main']//*//ul[@class='list_tabs']//li/a""")
    time.sleep(1)
    movie_tab.click()
    movies = driver.find_elements('xpath', """.//div[@class='lister-list']//*//div[@class='title']//a""")
    movie_list = []
    for movie in movies:
        movie_name = movie.text
        movie_rank = movie.find_element('xpath', """.//parent::div//parent::div//div[@id='moviemeter']""")
        movie_rank = movie_rank.text.split(':')[1].strip()
        movie_url = movie.get_attribute('href')
        movie_list.append({'Name':movie_name, 'Rank':movie_rank, 'URL':movie_url})
    df_in_theaters = pd.DataFrame(movie_list)
    return df_in_theaters

""" Function that scrapes Top Box Office section """
def scrapeTopBoxOffice(driver):
    movies = driver.find_elements('xpath',""".//div[@id='boxoffice']//tbody//tr""")
    movie_list = []
    for movie in movies:
        movie_name = movie.find_element('xpath',""".//td[@class='titleColumn']""").text
        movie_url =  movie.find_element('xpath',""".//td//a""").get_attribute('href')
        ratings = movie.find_elements('xpath', """.//td[@class='ratingColumn']""")
        weekend = ratings[0].text
        gross = ratings[1].text
        weeks = movie.find_element('xpath', """.//td[@class='weeksColumn']""").text
        movie_list.append({'Name':movie_name, 'Weekend': weekend,
                           'Gross':gross, 'Weeks':weeks, 'URL':movie_url})
    df_top_box = pd.DataFrame(movie_list)
    return df_top_box

""" Function that scrapes Coming Soon section """
def scrapeComingSoon(driver):
    movies = driver.find_elements('xpath', """.//div[contains(@class,'list_item')]//
                                  td[@class='overview-top']""")
    movie_list = []
    for movie in movies:
        movie_name = movie.find_element('xpath', """.//h4//a""").text
        movie_url = movie.find_element('xpath', """.//h4//a""").get_attribute('href')
        director = movie.find_element('xpath', """.//div[@class='txt-block']//span """).text
        description = movie.find_element('xpath', """.//div[@class='outline'] """).text
        movie_list.append({'Name':movie_name, 'Director': director,
                           'Description':description, 'URL':movie_url})
    df_coming_soon = pd.DataFrame(movie_list)
    return df_coming_soon
