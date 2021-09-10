#NHL Dataset Generator, Uses NHL API calls to populate datasets

#currently generates all teams w/ roster in seperate .json files will make into 1 csv file in the future
#also generates goalie regular/playoff season datasets in a single csv per event

#position is only to seperate player stats from goalie stats, 'G' will generate goalie stats, 
#anything else will generate the players stats

#event is to seperate regular season stats from playoff stats choices are 'playoffs' and 'regular'

import requests
import json
import pandas as pd
from csv import writer
import os

class NhlGenerator:
    def __init__(self, position, event):
        self.team_id_name = {}
        self.player_links = {}
        self.position = position
        self.event = event
    
    #Creates json with NHL teams and the team info
    def team_request(self):
        nhlteams = requests.get('https://statsapi.web.nhl.com/api/v1/teams')
        nhlteams.raise_for_status()
        nhl_response = json.loads(nhlteams.content)

        #check if directory exists
        main_dir = os.path.isdir('nhldatasets')
        
        if not main_dir:
            os.makedirs('nhldatasets')
            os.makedirs('nhldatasets/players')
            print('Creating Directories... ')

            with open('nhldatasets/nhlteams.json', 'w') as teamids:
                json.dump(nhl_response, teamids, indent = 4)
        
            for idx in range(len(nhl_response['teams'])):
                team_id = nhl_response['teams'][idx]['id']
                team_name = nhl_response['teams'][idx]['name']    
    
                self.team_id_name.setdefault(team_id, team_name)

            self.generate_teams(self.team_id_name)
        
        else:
            for idx in range(len(nhl_response['teams'])):
                team_id = nhl_response['teams'][idx]['id']
                team_name = nhl_response['teams'][idx]['name']    
    
                self.team_id_name.setdefault(team_id, team_name)

            self.generate_players(self.team_id_name)
    
    #Creates a json for each team with the roster list and some info about the player.
    def generate_teams(self, teams_dict):
        for key, value in teams_dict.items():
            roster_req = requests.get('https://statsapi.web.nhl.com/api/v1/teams/{}/roster'.format(key))
            roster_req.raise_for_status()
            roster_response = json.loads(roster_req.content)
            with open('nhldatasets/' + value.lower().strip() + '.json', 'w') as rosterwriter:
                json.dump(roster_response, rosterwriter, indent = 4)

        self.generate_players(teams_dict)

    #Creates a single csv based on position and event variables of career statistics of all players/goalies
    def generate_players(self, teams_dict):
        id_list = list(teams_dict.keys())
        for idx in id_list:
            player_id_req = requests.get('https://statsapi.web.nhl.com/api/v1/teams/{}/roster'.format(idx))
            player_id_req.raise_for_status()
            player_id_response = json.loads(player_id_req.content)

            for idx in range(len(player_id_response['roster'])):
                if self.position == 'G':
                    if player_id_response['roster'][idx]['position']['code'] != 'G':
                        continue
                    else:
                        player_name = player_id_response['roster'][idx]['person']['fullName']
                        player_link = player_id_response['roster'][idx]['person']['link']
                else:
                    if player_id_response['roster'][idx]['position']['code'] == 'G':
                        continue
                    else:
                        player_name = player_id_response['roster'][idx]['person']['fullName']
                        player_link = player_id_response['roster'][idx]['person']['link']
                
                self.player_links.setdefault(player_name, player_link)
        
        if self.event == 'playoffs' and self.position == 'G':
            for key, value in self.player_links.items():
                player_stat_req = requests.get('https://statsapi.web.nhl.com/{}/stats?stats=careerPlayoffs'.format(value))
                player_stat_req.raise_for_status()
                player_stat_response = json.loads(player_stat_req.content)

                try:
                    player_stats = player_stat_response['stats'][0]['splits'][0]['stat']
                except IndexError:
                    continue
                player_df = pd.DataFrame(player_stats, index = [0])
        
                for idx in range(len(player_stat_response['stats'][0]['splits'])):
                    file_exists = os.path.isfile('nhldatasets/players/careergoalieplayoffseason.csv')
                    player_stats = player_stat_response['stats'][0]['splits'][idx]['stat']
                    player_df['fullName'] = key
        
                if not file_exists:
                    player_df.to_csv('nhldatasets/players/careergoalieplayoffseason.csv', index = False)
                else:
                    player_df.to_csv('nhldatasets/players/careergoalieplayoffseason.csv', index = False, mode = 'a', header = False)
        
        elif self.event == 'regular' and self.position == 'G':
            for key, value in self.player_links.items():
                player_stat_req = requests.get('https://statsapi.web.nhl.com/{}/stats?stats=careerRegularSeason'.format(value))
                player_stat_req.raise_for_status()
                player_stat_response = json.loads(player_stat_req.content)

                try:
                    player_stats = player_stat_response['stats'][0]['splits'][0]['stat']
                except IndexError:
                    continue
                player_df = pd.DataFrame(player_stats, index = [0])
        
                for idx in range(len(player_stat_response['stats'][0]['splits'])):
                    file_exists = os.path.isfile('nhldatasets/calgaryplayers/careergoalieregseason.csv')
                    player_stats = player_stat_response['stats'][0]['splits'][idx]['stat']
                    player_df['fullName'] = key
        
                if not file_exists:
                    player_df.to_csv('nhldatasets/players/careergoalieregseason.csv', index = False)
                else:
                    player_df.to_csv('nhldatasets/players/careergoalieregseason.csv', index = False, mode = 'a', header = False)
        
        elif self.event == 'playoffs' and self.position != 'G':
            for key, value in self.player_links.items():
                player_stat_req = requests.get('https://statsapi.web.nhl.com/{}/stats?stats=careerPlayoffs'.format(value))
                player_stat_req.raise_for_status()
                player_stat_response = json.loads(player_stat_req.content)

                try:
                    player_stats = player_stat_response['stats'][0]['splits'][0]['stat']
                except IndexError:
                    continue
                player_df = pd.DataFrame(player_stats, index = [0])
        
                for idx in range(len(player_stat_response['stats'][0]['splits'])):
                    file_exists = os.path.isfile('nhldatasets/calgaryplayers/careerplayoffseason.csv')
                    player_stats = player_stat_response['stats'][0]['splits'][idx]['stat']
                    player_df['fullName'] = key
        
                if not file_exists:
                    player_df.to_csv('nhldatasets/players/careerplayoffseason.csv', index = False)
                else:
                    player_df.to_csv('nhldatasets/players/careerplayoffseason.csv', index = False, mode = 'a', header = False)
        
        elif self.event == 'regular' and self.position != 'G':
            for key, value in self.player_links.items():
                player_stat_req = requests.get('https://statsapi.web.nhl.com/{}/stats?stats=careerRegularSeason'.format(value))
                player_stat_req.raise_for_status()
                player_stat_response = json.loads(player_stat_req.content)

                try:
                    player_stats = player_stat_response['stats'][0]['splits'][0]['stat']
                except IndexError:
                    continue
                player_df = pd.DataFrame(player_stats, index = [0])
        
                for idx in range(len(player_stat_response['stats'][0]['splits'])):
                    file_exists = os.path.isfile('nhldatasets/calgaryplayers/careerregseason.csv')
                    player_stats = player_stat_response['stats'][0]['splits'][idx]['stat']
                    player_df['fullName'] = key
        
                if not file_exists:
                    player_df.to_csv('nhldatasets/players/careerregseason.csv', index = False)
                else:
                    player_df.to_csv('nhldatasets/players/careerregseason.csv', index = False, mode = 'a', header = False)

        else:
            print('Invalid Option')

if __name__ == '__main__':
    start_gen = NhlGenerator('a', 'playoffs')
    start_gen.team_request()
    
