# -*- coding: utf-8 -*-
"""
Created on Sun Nov 27 08:25:15 2022

@author: Cory
"""
import pandas as pd
import numpy as np

df = pd.read_csv('your_df.csv', low_memory=False)

# indicate whether or not your want the dataframe to include first basket data only
# if false, datrame will also include tipoff info for available games
first_baskets_only = False

def get_first_basket_and_tipoff_df(df, first_baskets_only, remove_unknown_jumps=True):
    '''
    Constructs a dataframe with first basket and tipoff plays for a
    given game in a single row. This also includes free throw shots as
    the first made shot of the game. Dataframe does not include jump balls that
    resulted in violations.

    Parameters
    ----------
    df : dataframe containing play-by-play data for NBA games
    first_baskets_only : (bool) whether or not to include a dataframe only consisting of 
                        first basket data for every NBA or to also include tipoff data too
    remove_unknown_jumps : (bool) to include unknown jump results in the dataframe. 
                            Default is to not include unknown jump results
    Returns
    -------
    first baskets dataframe or first baskets with tipoffs dataframe

    '''
    
    # retrieve all first basket plays from the dataframe
    first_basket_df = df.loc[((df['AwayScore'] == 2) & (df['HomeScore'] == 0) & (df['ShotOutcome'] == 'make') & (df['ShotType'].str.contains('2-pt'))) # 2 point shot was made by away team
            | ((df['AwayScore'] == 0) & (df['HomeScore'] == 2) & (df['ShotOutcome'] == 'make') & (df['ShotType'].str.contains('2-pt'))) # 2 point shot was made by home team
            | ((df['AwayScore'] == 1) & (df['HomeScore'] == 0) & (df['FreeThrowOutcome'] == 'make')) # free throw made by away team
            | ((df['AwayScore'] == 0) & (df['HomeScore'] == 1) & (df['FreeThrowOutcome'] == 'make')) # free throw made by home team
            | ((df['AwayScore'] == 3) & (df['HomeScore'] == 0) & (df['ShotOutcome'] == 'make') & (df['ShotType'].str.contains('3-pt'))) # 3 point shot was made by away team 
            | ((df['AwayScore'] == 0) & (df['HomeScore'] == 3) & (df['ShotOutcome'] == 'make') & (df['ShotType'].str.contains('3-pt')))] # 3 point shot was made by home team  
    
    # remove unnecessary columns or columns that contain no data
    first_basket_drop_cols = [col for col in first_basket_df.columns if first_basket_df[col].isnull().all()]
    first_basket_drop_cols.extend(['Quarter','WinningTeam', 'ShotOutcome', 'FreeThrowOutcome'])
    first_basket_df.drop(columns=first_basket_drop_cols, inplace=True)
    
    # if you want the dataframe to only include the first basket plays
    if first_baskets_only:
        final_df = first_basket_df
    
    # else, get all tipoff results from every game and combine them with the first basket dataframe
    else:
        # retrieve all game tipoffs from the data frame that are not null or a violation
        tipoff_df = df.loc[(df['SecLeft'] == 720) & (df['Quarter'] == 1) & (df['JumpballPoss'].notnull()) & (df['JumpballPoss'] != 'Violation')] 
        
        # remove unnecessary columns or columns that contain no data
        tipoff_drop_cols = [col for col in tipoff_df.columns if tipoff_df[col].isnull().all()]
        tipoff_drop_cols.extend(['Quarter', 'SecLeft', 'AwayScore', 'HomeScore', 'FoulType', 'Fouler', 'Fouled', 'ViolationPlayer', 'ViolationType',
                            'Season_Year', 'GameType', 'Date', 'Time', 'WinningTeam', 'Location', 'AwayTeam', 'HomeTeam'])
        tipoff_df.drop(columns=tipoff_drop_cols, inplace=True)    
        
        # merge the first baskets and tipoff plays for each game into a single dataframe
        # also rename columns to indicate which place is the jump ball play and first basket play
        final_df = first_basket_df.merge(tipoff_df, how='inner', on='URL', suffixes=('_FirstBasket', '_JumpBall'))
        
        final_df.rename(columns={"HomePlay": "HomePlay_FirstBasket"}, inplace=True)
    
    # add first basket team
    for index, row in final_df.iterrows():
        away_team = row['AwayTeam']
        home_team = row['HomeTeam']
        away_score = row['AwayScore']
        home_score = row['HomeScore']
        
        if away_score == 0 and home_score > 0:
            final_df.at[index, 'FB_Team(Home or Away)'] = 'Home'
            final_df.at[index, 'FB_Team'] = home_team
        elif home_score == 0 and away_score > 0:
            final_df.at[index, 'FB_Team(Home or Away)'] = 'Away'
            final_df.at[index, 'FB_Team'] = away_team
    
    # if the jump result is unknown remove that game from the dataframe
    if remove_unknown_jumps and not first_baskets_only:
        final_df = final_df.loc[~final_df['JumpballTeamPoss(Home or Away)'].str.contains('Unknown')]
    
    return final_df

################################
################################

# get fraction of times taller player won jump ball

def apply_taller_player_won_tip(away_player_height, home_player_height, jump_team_won):
    '''
    Creates a column to indicate if taller player won the jump ball
    if players are the same height then 'same height' will be returned

    Parameters
    ----------
    away_player_height : (int)
    home_player_height : (int)
    jump_team_won : (str) 'Home' or 'Away', nan if a violation occured
        
    '''
    # if either players height is nan, then a jump ball violation occured
    if pd.isnull(away_player_height) or pd.isnull(home_player_height):
        return np.nan
    elif away_player_height > home_player_height and jump_team_won == 'Away':
        return 'Taller won'
    elif away_player_height > home_player_height and jump_team_won == 'Home':
        return 'Shorter won'
    elif home_player_height > away_player_height and jump_team_won == 'Home':
        return 'Taller won'
    elif home_player_height > away_player_height and jump_team_won == 'Away':
        return 'Shorter won'
    elif home_player_height == away_player_height:
        return 'Same Height'
    
################################
################################

# get fraction of times lighter player won jump ball

def apply_lighter_player_won_tip(away_player_weight, home_player_weight, jump_team_won):
    '''
    Creates a column to indicate if lighter player won the jump ball
    if players are the same height nan will be filled in column

    Parameters
    ----------
    away_player_weight : (int)
    home_player_weight : (int)
    jump_team_won : (str) 'Home' or 'Away', nan if weight not available

    '''
    if pd.isnull(away_player_weight) or pd.isnull(home_player_weight):
        return np.nan
    elif away_player_weight < home_player_weight and jump_team_won == 'Away':
        return 'Lighter won'
    elif away_player_weight < home_player_weight and jump_team_won == 'Home':
        return 'Heavier won'
    elif home_player_weight < away_player_weight and jump_team_won == 'Home':
        return 'Lighter won'
    elif home_player_weight < away_player_weight and jump_team_won == 'Away':
        return 'Heavier won'
    elif home_player_weight == away_player_weight:
        return 'Same Weight'
    
################################
################################

# apply function to indicate if jump ball player got the first basket

def jump_ball_player_got_first_basket(jumpball_away_player, jumpball_home_player, shooter, foul_shooter):
    '''
    return an indicator for whether or not either jump ball player got the first basket
    of the game. This includes foul shots. 

    '''
    jumpball_away_player = jumpball_away_player.split('-')[1].strip()
    jumpball_home_player = jumpball_home_player.split('-')[1].strip()
    
    # if first basket was a field goal
    if pd.isnull(foul_shooter) and pd.notnull(shooter):
        shooter = shooter.split('-')[1].strip()
        if jumpball_away_player == shooter or jumpball_home_player == shooter:
            return True
        else:
            return False
        
    # if first basket was a foul shot
    elif pd.notnull(foul_shooter) and pd.isnull(shooter):
        foul_shooter = foul_shooter.split('-')[1].strip()
        if jumpball_away_player == foul_shooter or jumpball_home_player == foul_shooter:
            return True
        else:
            return False
        
################################
################################

first_baskets_tipoff_df = get_first_basket_and_tipoff_df(df, first_baskets_only)

# add foul shot to shot type column for first baskets made via foul shot
first_baskets_tipoff_df.loc[first_baskets_tipoff_df['FreeThrowShooter'].notnull(), 'ShotType'] = 'Foul shot'

# if building a dataframe with tipoff data, add in feature columns
if not first_baskets_only:
    
    first_baskets_tipoff_df['TallerPlayerWonJump'] = first_baskets_tipoff_df.apply(lambda row : apply_taller_player_won_tip(row['JumpballAwayPlayer Height(in)'],
                          row['JumpballHomePlayer Height(in)'], row['JumpballTeamPoss(Home or Away)']), axis = 1)
    
    first_baskets_tipoff_df['LighterPlayerWonJump'] = first_baskets_tipoff_df.apply(lambda row : apply_lighter_player_won_tip(row['JumpballAwayPlayer Weight(lb)'],
                          row['JumpballHomePlayer Weight(lb)'], row['JumpballTeamPoss(Home or Away)']), axis = 1)
    
    first_baskets_tipoff_df['JumpPlayerGotFirstBasket'] = first_baskets_tipoff_df.apply(lambda row : jump_ball_player_got_first_basket(row['JumpballAwayPlayer'],
                          row['JumpballHomePlayer'], row['Shooter'], row['FreeThrowShooter']), axis = 1)
    
    # add indicator for team winning jump and getting the first basket of the game
    first_baskets_tipoff_df['WinJump & FirstBasket'] = (first_baskets_tipoff_df['JumpballTeamPoss(Home or Away)'] == first_baskets_tipoff_df['FB_Team(Home or Away)'])
    
    # save first basket with tipoff data frame to csv file     
    first_baskets_tipoff_df.to_csv('first_baskets_tipoff.csv', index=False)
    
else:
    # save first basket data frame to csv file     
    first_baskets_tipoff_df.to_csv('first_baskets.csv', index=False)