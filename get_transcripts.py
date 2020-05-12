from time import sleep

from psycopg2 import connect
from urllib import parse

from driver_factory import get_driver
from line import Line


driver = get_driver()
driver.implicitly_wait(1)

character_ids = {}

SELECTED_SEASON = 1

try:
    conn = connect('host=localhost dbname=spongebob user=postgres')
    cur = conn.cursor()
    cur.execute('SELECT tag, title, season_num FROM episodes WHERE season_num=%s ORDER BY tag ASC;', (SELECTED_SEASON,))
    # cur.execute('SELECT tag, title, season_num FROM episodes WHERE tag=%s ORDER BY tag ASC;', ('1a',))
    episodes = cur.fetchall()
    # episodes = cur.fetchmany(5)
    for episode in episodes:
        tag = episode[0]
        title = episode[1]

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
                    cur.execute('SELECT id FROM characters WHERE name=%s;', (character,))
                    character_result = cur.fetchone()
                    if character_result == None:
                        cur.execute('INSERT INTO characters (name) VALUES (%s) RETURNING id;', (character,))
                        character_result = cur.fetchone()
                    character_ids[character] = character_result[0]
            
                character_id = character_ids[character]

                cur.execute('INSERT INTO voice_lines (character_id, said_what, episode_tag, line_number) VALUES (%s, %s, %s, %s)',
                                (character_id, said_what, tag, i))

    conn.commit()
            
finally:
    driver.quit()
