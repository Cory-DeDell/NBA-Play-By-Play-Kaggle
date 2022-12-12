# -*- coding: utf-8 -*-
"""
Created on Sun Nov 27 08:25:15 2022

@author: Cory
"""
import pandas as pd
import numpy as np

# the code used to scrape and generate the kaggle data set
# sometimes incorrectly assigned the home jump ball player to
# the JumpballAwayPlayer column and vice versa for the away player
# the following code reassigns those players to the correct column

# load csv file from the kaggle data set
df = pd.read_csv('your_df.csv', low_memory=False)

# get all games in dataframe
games = df['URL'].unique()

# iterate through each game
for game in games:
    
    # generate dataframe containing only a single game from the games list
    game_df = df.loc[df['URL'] == game]
    
    # get the index and names of each away jump ball player
    jump_ball_away_ind = game_df.loc[game_df['JumpballAwayPlayer'].notnull()].index.tolist()
    # get list of all jump ball away players for the particular game
    jump_ball_away_players = game_df.loc[jump_ball_away_ind, 'JumpballAwayPlayer'].tolist()

    # get the index and names of each home jump ball player
    jump_ball_home_ind = game_df.loc[game_df['JumpballHomePlayer'].notnull()].index.tolist()
    # get list of all jump ball home players for the particular game
    jump_ball_home_players = game_df.loc[jump_ball_home_ind, 'JumpballHomePlayer'].tolist()
    
    # get a dataframe that consists of all home players involved in the game
    home_players_df = game_df.loc[(game_df['HomePlay'].notnull()) & ((game_df['Shooter'].notnull()) 
                            | (game_df['Rebounder'].notnull()) | (game_df['Assister'].notnull())
                            | (game_df['EnterGame'].notnull()) | (game_df['LeaveGame'].notnull()))]
    
    # get an array of all players involved in the game for the home team
    home_players = pd.unique(home_players_df[['Shooter', 'Rebounder', 'Assister', 'EnterGame', 'LeaveGame']].values.ravel('K'))

    # get a dataframe that consists of all away players involved in the game
    away_players_df = game_df.loc[(game_df['AwayPlay'].notnull()) & ((game_df['Shooter'].notnull()) 
                            | (game_df['Rebounder'].notnull()) | (game_df['Assister'].notnull())
                            | (game_df['EnterGame'].notnull()) | (game_df['LeaveGame'].notnull()))]
    
    # get an array of all players involved in the game for the away team
    away_players = pd.unique(away_players_df[['Shooter', 'Rebounder', 'Assister', 'EnterGame', 'LeaveGame']].values.ravel('K'))
    
    # iterate through the jump ball players and reassign them as needed
    for i, player in enumerate(jump_ball_away_players):
        if player in home_players:
            # player was incorrectly assigned to jump ball away, reassign to jump ball home
            df.at[jump_ball_away_ind[i], 'JumpballHomePlayer'] = player
        elif player in away_players:
            # player was correctly assigned, do nothing
            pass
        else:
            # player not found
            print(player)
            
    for i, player in enumerate(jump_ball_home_players):
        if player in away_players:
            # player was incorrectly assigned to jump ball home, reassign to jump ball away
            df.at[jump_ball_home_ind[i], 'JumpballAwayPlayer'] = player
        elif player in home_players:
            # player was correctly assigned, do nothing
            pass
        else:
            # player not found
            print(player)

# save updated data frame with corrected jump ball players to a csv file
# df.to_csv('your_df.csv', index=False)
