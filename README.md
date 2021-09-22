# nhlstats
statistics webpage for nhl

Python v3.9.0

pandas v1.1.4

requests v2.25.0

json v2.0.9

csv v1.0

2021-09-14: Added file to create SQL database that includes players table, divisions table, teams table and venues table
  all tables are assigned relations and have endpoints for more info included
  
  added player regular season career stats table, includes time on ice, shots, goals, assists, points etc..


Generates team list, all the teams w/ roster(minimal info) into seperate json files

generates career statistics, will be adding year by year in the future.

the event variable is to seperate regular season from the playoff statistics, choices are 'regular', 'playoffs'

the position variable is to seperate goalies from other player statistics, any option other than 'G' will generate the players while
'G' will generate the goalie statistics

currently 4 datasets in wideform from the nhl undocumented api

will be adding more in the future as well as visualizations

and lastly incorporate it all into a webpage
