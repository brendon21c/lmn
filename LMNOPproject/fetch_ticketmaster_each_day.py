from django.utils import timezone
from datetime import datetime, timedelta
import requests
import json
import logging
from lmn.keys import keys
import psycopg2
import os


try:

    import dj_database_url
    db_from_env = dj_database_url.config()
    DATABASES['default'].update(db_from_env)

    db = psycopg2.connect(database='lmnop', user='lmnop', password=os.environ['POSTGRES_LMNOP_USER_PASSWORD'], host=db_from_env)
    cur = db.cursor()

    # search = 'SELECT * FROM lmn_note'
    # cur.execute(search)
    # rows = cur.fetchall()
    # print(rows)

    # artist = 'Brendon McKeever'
    # cur.execute('SELECT * FROM lmn_artist WHERE name=%s', (artist,)) # TODO can't seem to figure out how to pass a string into query.
    # rows = cur.fetchall()
    # print(rows)
    # print(type(rows))

    # query = 'INSERT INTO lmn_artist (name) VALUES (%s)'
    # cur.execute(query, (artist,))
    # db.commit()


    # start the daily task of adding events to database from ticketmaster.
    base_url = 'https://app.ticketmaster.com/discovery/v2/events.json?apikey={}&startDateTime={}&endDateTime={}&stateCode=MN'

    key = keys['TM_KEY']

    # getting time and formatting it for ticketmaster.
    time = datetime.utcnow()
    start_time = time + timedelta(days=1) - timedelta(hours=5)
    final_start = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_time = time + timedelta(days=2) - timedelta(hours=5)
    final_end = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    print(final_start)
    print(final_end)


    url = base_url.format(key,final_start,final_end)

    response = requests.get(url)

    tm_json = response.json()

    #print(tm_json)



    show_list = dict()

    try:

        artist = tm_json["_embedded"]['events']


        # Loop over json and pull relevant info.
        for entry in artist:
            for place in entry["_embedded"]['venues']:
                for performer in entry["_embedded"]['attractions']:

                    artist = ''

                    #oddly I found that not every show has a attraction name.
                    try:
                        artist = performer['name']

                    except Exception as e:
                        artist = entry['name']

                    location = place['name']

                    cur.execute('SELECT * FROM lmn_venue WHERE name=%s', (location,))
                    venue_rows = cur.fetchall()

                    if not venue_rows:

                        city = place['city']['name']
                        print(location)
                        print(city)

                        query = 'INSERT INTO lmn_venue (name,city,state) VALUES (%s,%s,%s)'
                        cur.execute(query, (location, city, 'MN'))
                        db.commit()

                    day = entry["dates"]["start"]["localDate"]
                    time = entry["dates"]["start"]["localTime"]

                    date_time = day + " " + time

                    venue_list = []

                    venue_list.append(location)
                    venue_list.append(date_time)

                    show_list[artist] = venue_list


        #print(show_list)

        value_list = []

        # loop over created dictionary and add show/artist to database.
        for key, value in show_list.items():

            name = key
            value_list = show_list[key]
            location = value_list[0]
            date = value_list[1]
            print(date)

            cur.execute('SELECT * FROM lmn_artist WHERE name=%s', (name,))
            artist_rows = cur.fetchall()

            cur.execute('SELECT * FROM lmn_venue WHERE name=%s', (location,))
            venue_rows = cur.fetchall()

            artist_id = 0
            venue_id = 0

            #check if artist is in database.
            if not artist_rows:

                query = 'INSERT INTO lmn_artist (name) VALUES (%s)'
                cur.execute(query, (name,))
                db.commit()

            #need to get artist ID to enter show information.
            cur.execute('SELECT * FROM lmn_artist WHERE name=%s', (name,))
            artist_rows = cur.fetchall()
            artist_id = artist_rows[0][0]

            cur.execute('SELECT * FROM lmn_venue WHERE name=%s', (location,))
            venue_rows = cur.fetchall()
            venue_id = venue_rows[0][0]

            # print(artist_id)
            # print(venue_id)

            #check if show has been created.
            cur.execute('SELECT * FROM lmn_show WHERE show_date=%s AND artist_id=%s AND venue_id=%s', (date,artist_id,venue_id,))
            event_rows = cur.fetchall()

            if not event_rows:

                query = 'INSERT INTO lmn_show (show_date,artist_id,venue_id) VALUES (%s,%s,%s)'
                cur.execute(query, (date, artist_id, venue_id))
                db.commit()

        cur.execute('SELECT * FROM lmn_show')
        event_rows = cur.fetchall()
        print(event_rows)

    except Exception as e:

        logging.exception("Problem!")

except Exception as e:
    logging.exception('problem connecting toi database.')
