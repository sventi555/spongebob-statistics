from time import sleep

from psycopg2 import connect
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from driver_factory import get_driver

driver = get_driver()
driver.get('https://spongebob.fandom.com/wiki/List_of_transcripts')

NUM_SEASONS = 12

try:
    seasons = driver.find_elements_by_xpath('//table[@class="wikitable"]')
    conn = connect('host=localhost dbname=spongebob user=postgres')
    cur = conn.cursor()
    for i in range(NUM_SEASONS):
        season = seasons[i]
        season_num = i + 1
        
        cur.execute('INSERT INTO seasons (num, episode_count) VALUES (%s, %s)', (season_num, 0))

        episodes = season.find_elements_by_xpath('./tbody/tr')

        for episode in episodes[1:]:
            tag = episode.find_element_by_xpath('./td[1]').text
            title = episode.find_element_by_xpath('./td[2]').text
            print('adding: ' + tag + '-' + title)
            cur.execute('INSERT INTO episodes (tag, title, season_num) VALUES (%s, %s, %s)', (tag, title, season_num))

    conn.commit()

finally:
    driver.quit()
