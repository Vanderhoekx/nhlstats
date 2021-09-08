import requests
import json
import pandas as pd
from csv import writer
import os

def generate_teams(teams_dict):
    for key, value in teams_dict.items():
        roster_req = requests.get('https://statsapi.web.nhl.com/api/v1/teams/{}/roster'.format(value))
        roster_response = json.loads(roster_req.content)
        with open('nhldatasets/' + key.lower().strip() + '.json', 'w') as rosterwriter:
            json.dump(roster_response, rosterwriter, indent = 4)

nhlteams = requests.get('https://statsapi.web.nhl.com/api/v1/teams')
nhlteams.raise_for_status()

nhl_response = json.loads(nhlteams.content)
team_id_name = {}
for idx in range(len(nhl_response['teams'])):
    team_id = nhl_response['teams'][idx]['id']
    team_name = nhl_response['teams'][idx]['name']    
    
    team_id_name.setdefault(team_id, team_name)

#generate_teams(team_id_name)

#team IDs
#{1: 'New Jersey Devils', 2: 'New York Islanders', 3: 'New York Rangers', 4: 'Philadelphia Flyers', 5: 'Pittsburgh Penguins', 6: 'Boston Bruins', 7: 'Buffalo Sabres', 
# 8: 'Montréal Canadiens', 9: 'Ottawa Senators', 10: 'Toronto Maple Leafs', 12: 'Carolina Hurricanes', 13: 'Florida Panthers', 14: 'Tampa Bay Lightning', 15: 'Washington Capitals', 
# 16: 'Chicago Blackhawks', 17: 'Detroit Red Wings', 18: 'Nashville Predators', 19: 'St. Louis Blues', 20: 'Calgary Flames', 21: 'Colorado Avalanche', 22: 'Edmonton Oilers', 
# 23: 'Vancouver Canucks', 24: 'Anaheim Ducks', 25: 'Dallas Stars', 26: 'Los Angeles Kings', 28: 'San Jose Sharks', 29: 'Columbus Blue Jackets', 30: 'Minnesota Wild', 52: 'Winnipeg Jets', 
# 53: 'Arizona Coyotes', 54: 'Vegas Golden Knights', 55: 'Seattle Kraken'}
id_list = list(team_id_name.keys())
for idx in id_list:
    player_id_req = requests.get('https://statsapi.web.nhl.com/api/v1/teams/{}/roster'.format(idx))
    player_id_response = json.loads(player_id_req.content)

#{'person': {'id': 8482067, 'fullName': 'Connor Mackey', 'link': '/api/v1/people/8482067'}, 'jerseyNumber': '3', 'position': {'code': 'D', 'name': 'Defenseman', 'type': 'Defenseman', 'abbreviation': 'D'}}
    player_links = {}


    # for idx in range(len(player_id_response['roster'])):
    #     if player_id_response['roster'][idx]['position']['code'] == 'G':
    #         continue
    #     else:
    #         player_name = player_id_response['roster'][idx]['person']['fullName']
    #         player_link = player_id_response['roster'][idx]['person']['link']
        
        # player_links.setdefault(player_name, player_link)

    for idx in range(len(player_id_response['roster'])):
        if player_id_response['roster'][idx]['position']['code'] != 'G':
            continue
        else:
            player_name = player_id_response['roster'][idx]['person']['fullName']
            player_link = player_id_response['roster'][idx]['person']['link']
        
        player_links.setdefault(player_name, player_link)
    
    for key, value in player_links.items():
        player_stat_req = requests.get('https://statsapi.web.nhl.com/{}/stats?stats=careerPlayoffs'.format(value))
        player_stat_response = json.loads(player_stat_req.content)

    # for key, value in player_links.items():
    #     player_stat_req = requests.get('https://statsapi.web.nhl.com/{}/stats?stats=careerPlayoffs'.format(value))
    #     player_stat_response = json.loads(player_stat_req.content)    

        try:
            player_stats = player_stat_response['stats'][0]['splits'][0]['stat']
        except IndexError:
            continue
        player_df = pd.DataFrame(player_stats, index = [0])
        
        for idx in range(len(player_stat_response['stats'][0]['splits'])):
            file_exists = os.path.isfile('nhldatasets/calgaryplayers/careergoalieplayoffseason.csv')
            player_stats = player_stat_response['stats'][0]['splits'][idx]['stat']
            #player_df = pd.DataFrame.append(player_df, player_stats, ignore_index = True)
            player_df['fullName'] = key
        
        if not file_exists:
            player_df.to_csv('nhldatasets/calgaryplayers/careergoalieplayoffseason.csv', index = False)
        else:
            player_df.to_csv('nhldatasets/calgaryplayers/careergoalieplayoffseason.csv', index = False, mode = 'a', header = False)

        # for idx in range(len(player_stat_response['stats'][0]['splits'])):
        #     file_exists = os.path.isfile('nhldatasets/calgaryplayers/careerplayoffseason.csv')
        #     player_stats = player_stat_response['stats'][0]['splits'][idx]['stat']
        #     #player_df = pd.DataFrame.append(player_df, player_stats, ignore_index = True)
        #     player_df['fullName'] = key
        
        # if not file_exists:
        #     player_df.to_csv('nhldatasets/calgaryplayers/careerplayoffseason.csv', index = False)
        # else:
        #     player_df.to_csv('nhldatasets/calgaryplayers/careerplayoffseason.csv', index = False, mode = 'a', header = False)