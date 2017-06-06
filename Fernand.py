import os
import speech_recognition as sr
import pyttsx
import time
import timestring
import gensim
import pyowm
import vlc
import wikipedia
import Youtube_Player
from Functions import (
    get_hour,
    get_date,
    get_weather,
    get_temperatures,
    set_a_reminder,
    play_the_radio,
    stop,
    read_RSS_feed,
    play_podcast,
    read_wikipedia_summary_article,
    look_wikipedia_related_articles,
    read_full_wikipedia_article,
    run_youtube_playlist,
    next_youtube_song,
    previous_youtube_song,
    turn_off,
    download_music,
    )
from Assistant import personal_assistant,ACTION,PARAMETERS
# Weather assistant
key = open("Keys/OWM_KEY.txt","r").read()
owm = pyowm.OWM(key,language='en')
# Word2Vec
word2vec_model_path = "W2V_model.bin"
huge_w2v_model_path = "Models/glove.6B.300d.bin"
# Links for other projects https://github.com/3Top/word2vec-api#where-to-get-a-pretrained-models
# https://github.com/facebookresearch/fastText/blob/master/pretrained-vectors.md?utm_campaign=buffer&utm_content=buffer0df9b&utm_medium=social&utm_source=linkedin.com
# Synthesizer
pyttx_engine = pyttsx.init()
# Speech recognition
speech_recognizer = sr.Recognizer()
speech_recognition_microphone = sr.Microphone
# Radio
instance = vlc.Instance()
player = instance.media_player_new()
radios = {"france culture": "http://direct.franceculture.fr/live/franceculture-midfi.mp3",
          "bolivia": "http://realserver5.megalink.com:8070",
          'nostalgie':"http://cdn.nrjaudio.fm/audio1/fr/40039/aac_64.mp3",
          'jazz':"http://jazz-wr01.ice.infomaniak.ch/jazz-wr01-128.mp3",
          'classique':"http://classiquefm.ice.infomaniak.ch/classiquefm.mp3",
          }

# RSS reader
rss_feeds = {"news": "http://feeds.bbci.co.uk/news/rss.xml?edition=uk#"}
number_records_to_read = 10

# Play podcast
podcasts_feeds = {'tech news today': 'http://feeds.twit.tv/tnt.xml',
                  'france culture': 'feed://radiofrance-podcast.net/podcast09/rss_10351.xml',
                  'nature':'http://feeds.nature.com/nature/podcast/current'}
podcast_index = 0

# Youtube player
youtube_player = Youtube_Player.youtube_player(instance,player)


actions_dict = {"hour" : {ACTION: get_hour, PARAMETERS: (time,)},
                "date" : {ACTION: get_date, PARAMETERS: (time,)},
                "weather": {ACTION: get_weather, PARAMETERS: (owm,)},
                "temperature": {ACTION: get_temperatures, PARAMETERS:(owm,)},
                "start radio":{ACTION:play_the_radio, PARAMETERS:(radios,player,instance)},
                "stop":{ACTION:stop, PARAMETERS:(youtube_player, player)},
                "rss feed":{ACTION:read_RSS_feed,PARAMETERS:(player, instance,rss_feeds,number_records_to_read)},
                "podcast":{ACTION:play_podcast,PARAMETERS:(player,instance,podcasts_feeds,podcast_index)},
                "wikipedia full":{ACTION:read_full_wikipedia_article,PARAMETERS:(player,instance,wikipedia)},
                "wikipedia summary":{ACTION:read_wikipedia_summary_article,PARAMETERS:(player,instance,wikipedia)},
                "wikipedia related":{ACTION:look_wikipedia_related_articles,PARAMETERS:(player,instance,wikipedia)},
                "youtube playlist":{ACTION:run_youtube_playlist,PARAMETERS:(youtube_player,)},
                "previous youtube song":{ACTION:previous_youtube_song,PARAMETERS:(youtube_player,)},
                "next youtube song":{ACTION:next_youtube_song,PARAMETERS:(youtube_player,)},
                "turn off":{ACTION:turn_off,PARAMETERS:()},
                "download audio":{ACTION:download_music,PARAMETERS:(youtube_player,)},
                }

trigger_dict = {"hour": "Tell me the hour. What time is it.",
                "date": "Tell me the date date. Which day is today.",
                "weather": "Tell me the weather. How is the weather. How is the climate. Tell me the actual temperature. How is the weather today",
                "temperature": "Tell me the weather forecast for today. How will be the temperature latter. Tell me the maximal and minimal temperature",
                "start radio": "Play the radio. Radio on. Turn on the radio.",
                "stop": "stop. Enough. Shut up. stop the radio. stop the music. stop reading.",
                "rss feed":"Read me an rss feed. Read me the news.",
                "podcast":"Play a podcast station. I want to head a podcast emission",
                "wikipedia full":"Read me a wikipedia article. Read me an entire article.",
                "wikipedia summary":"Look for a definition. Give the the summary of a wikipedia article. Read a definition from wikipedia?",
                "wikipedia related":"Look for related articles in wikipedia. Search related topics in wikipedia.",
                "youtube playlist":"search a playlist in youtube. I want to hear some music from youtube",
                "previous youtube song":"previous youtube song.",
                "next youtube song":"next youtube song.",
                "turn off":"bye. turn off. shutdow. die.",
                "download audio":"download audio from youtube.",
                }

confirmation_threshold = 0.3

centroid_shelve_file_name = "centroids_shelve"

# Personal Assistant
fernand = personal_assistant(word2vec_model_path,
                             pyttx_engine,
                             speech_recognition_microphone,
                             speech_recognizer,
                             actions_dict,
                             trigger_dict,
                             confirmation_threshold,
                             centroid_shelve_file_name,
                             huge_w2v_model_path)


for i in range(10000000):
    print i
    fernand.interactive_step()
