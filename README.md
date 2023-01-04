# NBA-Play-By-Play-Kaggle
This repository contains code to wrangle and analyze first basket data from the 'NBA Play-by-Play Data 2015-2021' dataset on Kaggle.

# Correction to kaggle data
During my initial review of the raw play-by-play data, I noticed that players listed under 'JumpballAwayPlayer' and 'JumpballHomePlayer'
were the correct players involved in the jump ball, but some were incorrectly labeled as away player when they were the home player
and vice versa. NBA_Data_Jump_Ball_Player_Correction.py corrects this issue by collecting all of the home and away players involved
in a given game and reassigns the jump ball players to the correct home/away column, if necessary.

# First basket and tipoff filter
NBA_Data_FB_tipoff_Filter.py takes the raw play-by-play data and returns a dataframe that contains all of the first basket plays along with
the tipoff play info (merged into a single row for a given game). You can also choose to return a dataframe that inlcudes only the first basket plays
without tipoff data.

# First basket data exploration
NBA_First_Basket_Analysis.ipynb performs some data exploration tasks and creates useful visualizations of the data
