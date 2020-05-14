from time import sleep

from elasticsearch import Elasticsearch
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from driver_factory import get_driver

driver = get_driver()
driver.get('https://spongebob.fandom.com/wiki/List_of_transcripts')

NUM_SEASONS = 12

try:
    seasons = driver.find_elements_by_xpath('//table[@class="wikitable"]')
    
    es = Elasticsearch()
    es.indices.create(index='seasons', ignore=[400])
    es.indices.create(index='episodes', ignore=[400])
    for i in range(NUM_SEASONS):
        season = seasons[i]
        season_num = i + 1
        
        es.index(index='seasons', body={'number': season_num})

        episodes = season.find_elements_by_xpath('./tbody/tr')

        for episode in episodes[1:]:
            tag = episode.find_element_by_xpath('./td[1]').text
            title = episode.find_element_by_xpath('./td[2]').text
            print('adding: ' + tag + '-' + title)
            es.index(index='episodes', body={'season_num': season_num, 'tag': tag, 'title': title})

finally:
    driver.quit()
