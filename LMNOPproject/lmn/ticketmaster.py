from django.shortcuts import render, redirect, get_object_or_404

from .models import Venue, Artist, Note, Show

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from django.utils import timezone
from datetime import datetime, timedelta

import requests
import json
import logging
from .keys import keys

def all_current_venues_response():

    base_url = 'https://app.ticketmaster.com/discovery/v2/events.json?apikey={}&size=500&stateCode=MN'

    key = keys['TM_KEY']

    url = base_url.format(key)

    response = requests.get(url)

    tm_json = response.json()

    return tm_json



# This class pulls data from ticketmaster and returns a dict of the Venues in Minnesota.
def get_all_current_venues():

    base_url = 'https://app.ticketmaster.com/discovery/v2/events.json?apikey={}&size=500&stateCode=MN'

    key = keys['TM_KEY']

    url = base_url.format(key)

    response = requests.get(url)

    tm_json = response.json()

    venue_list = dict()

    try:

        artist = tm_json["_embedded"]['events']

        for entry in artist:
            for place in entry["_embedded"]['venues']:

                location = place['name']
                city = place['city']['name']

                if location not in venue_list:

                    venue_list[location] = city


        return venue_list


    except Exception as e:

        logging.exception("Problem!")



def get_dates_for_artist(band_name):

    base_url = 'https://app.ticketmaster.com/discovery/v2/events.json?apikey={}&keyword={}&stateCode=MN'

    key = keys['TM_KEY']

    url = base_url.format(key, band_name)

    response = requests.get(url)

    tm_json = response.json()

    show_list = dict()


    # Error check to see if the JSON found a event in Minnesota.
    try:

        artist = tm_json["_embedded"]['events']

    except Exception as e:

        print("no band found")

        return None


    try:

        artist = tm_json["_embedded"]['events']

        # Loop over json and pull relevant info.
        for entry in artist:
            for place in entry["_embedded"]['venues']:
                for artists in entry["_embedded"]['attractions']:

                    artist = artists['name']
                    location = place['name']
                    day = entry["dates"]["start"]["localDate"]
                    time = entry["dates"]["start"]["localTime"]

                    date_time = day + " " + time

                    print(date_time)

                    venue_list = []

                    venue_list.append(location)
                    venue_list.append(date_time)

                    show_list[artist] = venue_list


        value_list = []

        print(show_list)

        # simple string to return to the view so that the program knows what to display.
        result_code = ''

        # loop over created dictionary and add show/artist to database.
        for key, value in show_list.items():

            name = key
            value_list = show_list[key]
            location = value_list[0]
            date = value_list[1]


            artist_query = Artist.objects.filter(name = name)

            # checks to see if artist doesn't exist in database
            if not artist_query:

                #print("no artist found")
                artist = Artist.objects.create(name = name)


            artist_query = Artist.objects.filter(name = name)

            venue_query = Venue.objects.filter(name = location)

            show_query = Show.objects.filter(show_date = date).filter(artist = artist_query[0]).filter(venue = venue_query[0])

            # if the show hasn't been created.
            if not show_query:


                entry = Show.objects.create(show_date = date, artist = artist_query[0], venue = venue_query[0])
                result_code = "entered"

        
            else:

                query = Show.objects.filter(show_date = date).filter(artist = artist_query[0]).filter(venue = venue_query[0])

                result_code = "already"




    except Exception as e:

        logging.exception("Problem!")

# start the daily task of adding events to database from ticketmaster.
def get_next_day_events():


    base_url = 'https://app.ticketmaster.com/discovery/v2/events.json?apikey={}&startDateTime={}&endDateTime={}&stateCode=MN'

    key = keys['TM_KEY']

    # getting time and formatting it for ticketmaster.
    time = datetime.utcnow()
    start_time = time + timedelta(days=1) - timedelta(hours=10)
    final_start = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_time = time + timedelta(days=2) - timedelta(hours=10)
    final_end = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")


    url = base_url.format(key,final_start,final_end)

    response = requests.get(url)

    tm_json = response.json()

    print(tm_json)



    show_list = dict()

    try:

        artist = tm_json["_embedded"]['events']

        # Loop over json and pull relevant info.
        for entry in artist:
            for place in entry["_embedded"]['venues']:
                for artists in entry["_embedded"]['attractions']:

                    artist = artists['name']
                    location = place['name']
                    day = entry["dates"]["start"]["localDate"]
                    time = entry["dates"]["start"]["localTime"]

                    date_time = day + " " + time

                    venue_list = []

                    venue_list.append(location)
                    venue_list.append(date_time)

                    show_list[artist] = venue_list


        print(show_list)

        value_list = []

        # loop over created dictionary and add show/artist to database.
        for key, value in show_list.items():

            name = key
            value_list = show_list[key]
            location = value_list[0]
            date = value_list[1]


            artist_query = Artist.objects.filter(name = name)
            venue_query = Venue.objects.filter(name = location)
            print(artist_query)

            # two checks to see if artist or venue don;t exist in database
            if not artist_query:

                #print("no artist found")
                artist = Artist.objects.create(name = name)

            artist_query = Artist.objects.filter(name = name)

            show_query = Show.objects.filter(show_date = date).filter(artist = artist_query[0]).filter(venue = venue_query[0])

            # if the show hasn't been created.
            if not show_query:

                entry = Show.objects.create(show_date = date, artist = artist_query[0], venue = venue_query[0])



    except Exception as e:

        logging.exception("Problem!")
