import requests
import json
import sqlite3 as sql

#populate the players table
def populate_team(roster, team_id):
    #create players table
    curr.execute('''CREATE TABLE IF NOT EXISTS players (
        player_id integer, 
        team_id integer, 
        full_name text, 
        position text, 
        player_endpoint text,
        FOREIGN KEY(team_id) REFERENCES teams(team_id))''')
    
    #insert values into table
    for id in roster['roster']:
        curr.execute('INSERT INTO players VALUES({}, {}, "{}", "{}", "{}")'.format(
            id['person']['id'],
            team_id,
            id['person']['fullName'],
            id['position']['abbreviation'],
            id['person']['link']
        ))
        player_ids.append(id['person']['id'])
    connection.commit()
    return player_ids

def career_reg_season_player(player_api_call, player_id):
    curr.execute('''CREATE TABLE IF NOT EXISTS careerregplayers (
        player_id integer,
        time_on_ice time,
        shots integer,
        goals integer,
        assists integer,
        games integer,
        hits integer,
        plusminus integer,
        FOREIGN KEY(player_id) REFERENCES players(player_id))''')
    try:
        for stat in player_api_call['stats']:
            print(stat['splits'][0]['stat'])
            curr.execute('INSERT INTO careerregplayers VALUES({}, "{}", {}, {}, {}, {}, {}, {})'.format(
                player_id,
                stat['splits'][0]['stat']['timeOnIce'],
                stat['splits'][0]['stat']['shots'],
                stat['splits'][0]['stat']['goals'],
                stat['splits'][0]['stat']['assists'],
                stat['splits'][0]['stat']['games'],
                stat['splits'][0]['stat']['hits'],
                stat['splits'][0]['stat']['plusMinus']
            ))
    except IndexError:
        pass
    connection.commit()
        
#send request for api response
team_request = requests.get('https://statsapi.web.nhl.com/api/v1/teams')
team_request.raise_for_status()

#parse response into a json
team_response = json.loads(team_request.content)

#used to call team_id on populate_team function
team_ids = []
player_ids = []

#create connection, database and cursor to work
connection = sql.connect(r'Sql\databases\nhlstats.db')
curr = connection.cursor()

tables_list = curr.execute('''SELECT name FROM sqlite_master WHERE type = "table" AND name = "venues"''').fetchall()
if len(tables_list) < 1:

#create divisions table
    curr.execute('''CREATE TABLE IF NOT EXISTS divisions (
        div_id integer,
        div_name text,
        div_abbr text,
        div_endpoint text,
        conf_id integer,
        conf_name text,
        conf_endpoint text
    )''')

    #create teams table
    curr.execute('''CREATE TABLE IF NOT EXISTS teams (
        team_id integer, 
        div_id integer,
        team_abb text, 
        team_name text,
        team_endpoint text,
        team_website text,
        FOREIGN KEY(div_id) REFERENCES divisions(div_id))''')

    #create venues table
    curr.execute('''CREATE TABLE IF NOT EXISTS venues (
        team_id integer,
        venue_name text,
        venue_location text,
        venue_endpoint text,
        FOREIGN KEY(team_id) REFERENCES teams(team_id))''')

#loop through api response and insert values into tables

    for id in range(len(team_response['teams'])):
        curr.execute('INSERT INTO divisions VALUES ({}, "{}", "{}", "{}", {}, "{}", "{}")'.format(
            team_response['teams'][id]['division']['id'],
            team_response['teams'][id]['division']['name'],
            team_response['teams'][id]['division']['abbreviation'],
            team_response['teams'][id]['division']['link'],
            team_response['teams'][id]['conference']['id'],
            team_response['teams'][id]['conference']['name'],
            team_response['teams'][id]['conference']['link']
        ))
        
        curr.execute('INSERT INTO teams VALUES ({}, {}, "{}", "{}", "{}", "{}")'.format(
            team_response['teams'][id]['id'],
            team_response['teams'][id]['division']['id'],
            team_response['teams'][id]['abbreviation'],
            team_response['teams'][id]['name'],
            team_response['teams'][id]['link'],
            team_response['teams'][id]['officialSiteUrl']
        ))

        curr.execute('INSERT INTO venues VALUES ({}, "{}", "{}", "{}")'.format(
            team_response['teams'][id]['id'],
            team_response['teams'][id]['venue']['name'],
            team_response['teams'][id]['venue']['city'],
            team_response['teams'][id]['venue']['link']
        ))  
        
        team_ids.append(team_response['teams'][id]['id'])
    #save the work
    connection.commit()

    #loop through team_ids list and call the endpoint to the function one at a time
    idx = 0
    while idx < len(team_ids):
        roster_request = requests.get('https://statsapi.web.nhl.com/api/v1/teams/{}/roster'.format(team_ids[idx]))
        roster_request.raise_for_status()

        roster_response = json.loads(roster_request.content)
        populate_team(roster_response, team_ids[idx])
        idx += 1

    player_details = curr.execute('''SELECT player_endpoint FROM players WHERE position NOT LIKE "G"''').fetchall()

    idx = 0
    while idx < len(player_details):
        
        player_reg_stats = requests.get('https://statsapi.web.nhl.com/{}/stats?stats=careerRegularSeason'.format(''.join(player_details[idx])))
        player_reg_stats.raise_for_status()
        
        player_response = json.loads(player_reg_stats.content)
        career_reg_season_player(player_response, player_ids[idx])
        idx += 1
