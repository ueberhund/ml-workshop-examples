import pandas as pd
import datetime
import time

def convert_to_unix(string_date):
    date_time_obj = datetime.datetime.strptime(string_date, '%Y-%m-%d')
    d = date_time_obj.date()
    return time.mktime(d.timetuple())

#Read in the data
airline_df = pd.read_csv('airline.csv')
interactions_df = airline_df.copy()
users_df = airline_df.copy()


#Create interactions dataset
interactions_df = interactions_df[['airline_name', 'author', 'date', 'cabin_flown', 'overall_rating']]
interactions_df['EVENT_TYPE']='RATING'
interactions_df['author'] = interactions_df['author'].str.replace(" ","")
interactions_df.rename(columns = {'airline_name':'ITEM_ID', 'author':'USER_ID',
                              'date':'TIMESTAMP', 'cabin_flown': 'CABIN_TYPE', 'overall_rating': 'EVENT_VALUE'}, inplace = True) 
interactions_df['TIMESTAMP'] = interactions_df['TIMESTAMP'].apply(convert_to_unix)
interactions_df = interactions_df.dropna()
interactions_df.to_csv('airline-interactions.csv', index=False, float_format='%.0f')


#Create users dataset
users_df = users_df[['author', 'author_country']]
users_df['author'] = users_df['author'].str.replace(" ","")
users_df.rename(columns = { 'author':'USER_ID', 'author_country':'NATIONALITY'}, inplace = True) 
users_df = users_df.dropna()
users_df.to_csv('airline-users.csv', index=False)