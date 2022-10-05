#!/usr/bin/env python
# coding: utf-8

# # Extract Data

# In[2]:


from googleapiclient.discovery import build
from datetime import datetime
from dateutil import parser
import pandas as pd

import seaborn as sb
import matplotlib.pyplot as plt


# In[3]:


api_key = ' '


# In[4]:


channel_ids = ['UCoOae5nYA7VqaXzerajD0lg']


# In[5]:


api_service_name = "youtube"
api_version = "v3"

    # Get credentials and create an API client
youtube = build(
    api_service_name, api_version, developerKey=api_key)


# In[6]:


def get_channel_stats(youtube, channel_ids):
    
    all_data = []
    

    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=','.join(channel_ids)
    )
    response = request.execute()
    
    for item in response['items']:
        data = {'channelName': item['snippet']['title'],
               'subscribers': item['statistics']['subscriberCount'],
                'views': item['statistics']['viewCount'],
                'totalViews': item['statistics']['videoCount'],
                'playlistId': item['contentDetails']['relatedPlaylists']['uploads']
               }
        
        all_data.append(data)
    return(pd.DataFrame(all_data))


# In[7]:


channel_stats = get_channel_stats(youtube, channel_ids)


# In[8]:


channel_stats


# In[9]:


playlist_id = "UUoOae5nYA7VqaXzerajD0lg"

def get_video_ids(youtube, playlist_id):
    
    video_ids = []
    
    request = youtube.playlistItems().list(
        part="snippet,contentDetails",
        playlistId="UUoOae5nYA7VqaXzerajD0lg",
        maxResults = 50
    )
    response = request.execute()
    
    for item in response['items']:
        video_ids.append(item['contentDetails']['videoId'])
        
    next_page_token = response.get('nextPageToken')
    
    while next_page_token is not None:
        request = youtube.playlistItems().list(
                    part = "snippet,contentDetails",
                    playlistId = playlist_id,
                    maxResults = 50,
                    pageToken = next_page_token)
        response = request.execute()
    
        for item in response['items']:
            video_ids.append(item['contentDetails']['videoId'])
        
        next_page_token = response.get('nextPageToken')
 
    
        
    return video_ids

print(response)


# In[10]:


video_ids = get_video_ids(youtube, playlist_id)


# In[11]:


len(video_ids)


# In[12]:


def get_video_details(youtube, video_ids):

    all_video_info = []
    
    for i in range(0, len(video_ids), 50):                 
        request = youtube.videos().list(
            part = "snippet,contentDetails,statistics",
            id = ','.join(video_ids[i:i+50])
        )
    response = request.execute()

    for video in response['items']:
        stats_to_keep = {
                        'snippet': ['channelTitle', 'title', 'description', 'tags', 'publishedAt'],
                        'statistics': ['viewCount', 'likeCount', 'favouriteCount', 'commentCount'],
                        'contentDetails': ['duration', 'definition', 'caption']
                        }

        video_info = {}
        video_info['video_id'] = video['id']

        for k in stats_to_keep.keys():
            for v in stats_to_keep[k]:
                try:
                    video_info[v] = video[k][v]
                except:
                    video_info[v] = None
                   
        all_video_info.append(video_info)

    return pd.DataFrame(all_video_info)


# In[13]:


video_df = get_video_details(youtube, video_ids)


# In[14]:


video_df


# # Data pre processing 

# In[15]:


video_df.isnull().any()


# In[16]:


video_df.dtypes


# In[17]:


numeric_cols = ['viewCount', 'likeCount', 'favouriteCount', 'commentCount']
video_df[numeric_cols] = video_df[numeric_cols].apply(pd.to_numeric, errors = 'coerce', axis = 1)


# In[18]:


video_df.dtypes


# In[19]:


# Publish day

video_df['publishedAt'] = video_df["publishedAt"].apply(lambda x: parser.parse(x))
video_df['publishedDay'] = video_df["publishedAt"].apply(lambda x: x.strftime("%A"))


# In[20]:


video_df['tagCount'] = video_df['tags'].apply(lambda x: 0 if x is None else len(x))


# In[21]:


video_df


# In[22]:


ax = sb.barplot(x = 'title', y = 'viewCount', data = video_df.sort_values('viewCount', ascending = False)[0:9])
plt.xticks(rotation = 90)


# In[23]:


ax = sb.barplot(x = 'title', y = 'viewCount', data = video_df.sort_values('viewCount', ascending = True)[0:9])
plt.xticks(rotation = 90)


# In[24]:


#Comment vs Views and Like vs Views

fig, ax = plt.subplots(1,2)
sb.scatterplot(data = video_df, x = 'commentCount', y = 'viewCount', ax = ax[0])
sb.scatterplot(data = video_df, x = 'likeCount', y = 'viewCount', ax = ax[1])


# In[26]:


#Publish Frequency (daywise)

day_df = pd.DataFrame(video_df['publishedDay'].value_counts())
weekdays = [ 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'] #python dosn't know sequence of days
day_df = day_df.reindex(weekdays)
ax = day_df.reset_index().plot.bar(x = 'index', y = 'publishedDay', rot = 0)


# In[ ]:




