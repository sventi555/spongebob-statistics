from time import sleep

from elasticsearch import Elasticsearch
from urllib import parse

from driver_factory import get_driver
from line import Line


driver = get_driver()
driver.implicitly_wait(1)

character_ids = {}

SELECTED_SEASON = 1

try:
    es = Elasticsearch()
    es.indices.create(index='voice_lines', ignore=[400])
    es.indices.create(index='characters', ignore=[400])
    episodes = es.search(index='episodes', body=
    { 'query':
        { 'bool': 
            { 'must': [
                { 'match': { 'season_num': SELECTED_SEASON } }
            ]}
        }
    })['hits']['hits']
    print(episodes)
    for episode in episodes:
        tag = episode['_source']['tag']
        title = episode['_source']['title']

        url = 'https://' + parse.quote(f'spongebob.fandom.com/wiki/{title}/transcript')
        driver.get(url)
        
        print('Processing script for: ' + driver.title)
        
        line_elems = driver.find_elements_by_xpath('//div[@id="mw-content-text"]/ul/li[b]')
        for i, line_elem in enumerate(line_elems):
            line_text = line_elem.text
            colon_index = line_text.find(':')
            who = line_text[:colon_index]
            said_what = line_text[colon_index + 1:]

            who = who.replace('&', 'and').replace(', and ', ', ').replace(' and ', ', ')
            characters = who.split(', ')
            
            for character in characters:
                if character not in character_ids:
                    character_query = \
                    { 'query':
                        { 'bool': 
                            { 'must': [
                                { 'match': { 'name': character } }
                            ]}
                        }
                    }
                    character_result = es.search(index='characters', body=character_query)['hits']['hits']
                    if character_result == []:
                        es.index(index='characters', body={'name': character}, refresh=True)
                        character_result = es.search(index='characters', body=character_query)['hits']['hits']
                    character_ids[character] = character_result[0]['_id']
            
                character_id = character_ids[character]

                es.index(index='voice_lines',
                    body={'character_id': character_id, 'said_what': said_what, 'episode_tag': tag, 'line_number': i})

finally:
    driver.quit()
