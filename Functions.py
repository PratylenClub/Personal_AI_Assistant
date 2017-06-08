import timestring
import shelve
import time
import feedparser
from gtts import gTTS
from unidecode import unidecode
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders
import imaplib

DEFAULT_RADIO = "http://direct.franceculture.fr/live/franceculture-midfi.mp3"
DEFAULT_RSS = "http://feeds.bbci.co.uk/news/rss.xml?edition=uk#"
DEFAULT_PODCAST = "feed://radiofrance-podcast.net/podcast09/rss_10351.xml"


def get_date(assistant,time):
    date = time.strftime("Day: %A %d. Month: %B. Year: %Y")
    assistant.speak(date)
    print date

def get_hour(assistant,time):
    hour = time.strftime("Hour: %H. Minutes: %M")
    assistant.speak(hour)
    print hour

def get_weather(assistant, owm):
    # change this to infer directly the name of the city from the sentence
    assistant.speak("Tell me the city")
    city = assistant.active_listen()
    assistant.speak("Very good, I sent my assistant to check how is the weather in "+city)
    obs_list = owm.weather_at_places(str(city),searchtype='like',limit=3)
    weather = obs_list[0].get_weather()
    assistant.speak("The weather in " +city+ " is: "+ weather.get_detailed_status())
    temperature = weather.get_temperature(unit='celsius') 
    assistant.speak("The actual temperature is: "+str(temperature['temp']) +" degrees.")

def get_temperatures(assistant, owm):
    # change this to infer directly the name of the city from the sentence
    assistant.speak("Tell me the city")
    city = assistant.active_listen()
    print city
    obs_list = owm.weather_at_places(str(city),searchtype='like',limit=3)
    weather = obs_list[0].get_weather()
    temperature_dict = {"temp_max": "The maximal temperature will be: ", 'temp': "The actual temperature is: ","temp_min": "The minimal temperature will be: "}
    temperature = weather.get_temperature(unit='celsius') 
    temperature_txt = ""
    for key in temperature_dict:
        temperature_txt += temperature_dict[key] + str(temperature[key]) +" degrees."
    assistant.speak(temperature_txt)

def set_a_reminder(assistant, reminder_shelve_file_name):
    reminders = shelve.open(reminder_shelve_file_name, writeback=True)
    assistant.speak("Tell me the date")
    msg = assistant.active_listen()
    date = timestring.Date(msg).to_unixtime()
    print date
    assistant.speak("Tell me the message")
    msg = assistant.active_listen()
    print msg
    reminders[date] = msg
    reminders.sync()
    reminders.close()

def play_the_radio(assistant, radios, player_vlc, instance_vlc):
    assistant.speak("Tell the name of the radio")
    msg = assistant.active_listen()
    if msg in radios.keys():
        media = instance_vlc.media_new(radios[msg])
    else:
        media = instance_vlc.media_new(DEFAULT_RADIO)
    player_vlc.set_media(media)
    player_vlc.play()

def stop(assistant, youtube_player, player):
    youtube_player.stop()
    player.stop()


def read_RSS_feed(assistant, player_vlc, instance_vlc, rss_dic, number_records_to_read):
    assistant.speak("Tell me the name of the rss feed")
    msg = assistant.active_listen()
    if msg in rss_dic.keys():
        rss = rss_dic[msg]
    else:
        rss = DEFAULT_RSS
    assistant.speak("ok! I am calling my assistant, she will read the RSS feed.")
    res = feedparser.parse(rss)
    number_records_in_feed = len(res.entries)
    if number_records_in_feed < number_records_to_read:
        number_records_to_read = number_records_in_feed
    entries_to_read = [entry.title_detail.value for entry in res.entries[0:number_records_to_read]]
    txt=". ".join(entries_to_read)
    read_nicely_text(txt, instance_vlc, player_vlc)
    '''
    for entry in entries_to_read:    
        assistant.speak(entry.title_detail.value)
        time.sleep(1)
    '''

def read_nicely_text(txt, instance_vlc, player_vlc):
    tts = gTTS(text=txt,lang='en')
    tts.save("rss_read.mp3")
    media = instance_vlc.media_new("rss_read.mp3")
    player_vlc.set_media(media)
    player_vlc.play()

def play_podcast(assistant, player_vlc, instance_vlc, podcast_dic, podcast_index=None):
    assistant.speak("Tell me the name of the podcast")
    msg = assistant.active_listen()
    if msg in podcast_dic.keys():
        rss = podcast_dic[msg]
    else:
        rss = DEFAULT_PODCAST
    assistant.speak("There you go!")
    res = feedparser.parse(rss)
    number_records_in_feed = len(res.entries)
    if podcast_index is None:
        podcast_index = random.randint(0,len(res.entries) - 1)
    if number_records_in_feed < podcast_index:
        podcast_index = number_records_in_feed
    href = ""
    for link in res.entries[podcast_index].links:
        if ".mp3" in link.href:
            href = link.href
            break
    if href != "":
        media = instance_vlc.media_new(href)
        player_vlc.set_media(media)
        player_vlc.play()
    else:
        assistant.speak("I am sorry, but the podcast requested is not available!")

def speed_change(sound, speed=1.0):
    # Manually override the frame_rate. This tells the computer how many
    # samples to play per second
    sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
        "frame_rate": int(sound.frame_rate * speed)
    })

    # convert the sound with altered frame rate to a standard frame rate
    # so that regular playback programs will work right. They often only
    # know how to play audio at standard frame rate (like 44.1k)
    return sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)

#slow_sound = speed_change(sound, 0.75)
#fast_sound = speed_change(sound, 1.25)

#file_handle = fast_sound.export("good2.mp3",
#                          format="mp3")
#                          tags={"album": "The Bends", "artist": "Radiohead"},
#                          cover="/path/to/albumcovers/radioheadthebends.jpg")

def unicode_to_suitable_str(unicode_txt):
    txt = unicode_txt.encode('utf-8')
    return unidecode(txt.decode("utf-8",errors="ignore"))

def read_wikipedia_summary_article(assistant, player_vlc, instance_vlc, wikipedia):
    assistant.speak("What do you want to search in wikipedia?")
    msg = assistant.active_listen()
    possibilities = wikipedia.search(msg)
    if possibilities == 0:
        assistant.speak("I am sorry but I found nothing in wikipedia")
    else:
        assistant.speak("Very good! Please wait, my assistant will read it!")
        txt =  unicode_to_suitable_str(wikipedia.summary(possibilities[0]))
        print txt
        read_nicely_text(txt, instance_vlc, player_vlc)

def look_wikipedia_related_articles(assistant, player_vlc, instance_vlc,wikipedia):
    assistant.speak("What do you want to search in wikipedia?")
    msg = assistant.active_listen()
    possibilities = wikipedia.search(msg)
    if possibilities >= 1:
        assistant.speak("There are "+str(len(possibilities))+" related articles.")
        assistant.speak("Please wait, my assistant will read them!")
        msg = assistant.active_listen()
        txt = unicode_to_suitable_str(". ".join([str(i)+". "+p for i,p in enumerate(possibilities)]))
        print txt
        read_nicely_text(txt, instance_vlc, player_vlc)
    else:
        assistant.speak("I am sorry but I found nothing in wikipedia")


def read_full_wikipedia_article(assistant, player_vlc, instance_vlc,wikipedia):
    assistant.speak("What do you want to search in wikipedia?")
    msg = assistant.active_listen()
    try:
        possibilities = wikipedia.search(msg)
        if possibilities == 0:
            assistant.speak("I am sorry but I found nothing in wikipedia")
        else:
            assistant.speak("Very good! I will ask my assistant to read you this article. please wait")
            article = wikipedia.page(possibilities[0])
            txt = article.title+article.content
            txt = unicode_to_suitable_str(txt)
            read_nicely_text(txt, instance_vlc, player_vlc)
    except:
        assistant.speak("I am sorry but an unexpected error has occured")

def run_youtube_playlist(assistant, youtube_player):
    assistant.speak("Which playlist do you want me to search in youtube?")
    msg = assistant.active_listen()
    youtube_player.play_youtube_playlist(msg)  

def download_music(assistant, youtube_player):
    assistant.speak("Which song do you want to download?")
    msg = assistant.active_listen()
    youtube_player.download_song(msg)  

def next_youtube_song(assistant,youtube_player):
    youtube_player.next_song()

def previous_youtube_song(assistant,youtube_player):
    youtube_player.previous_song()

def turn_off(assistant):
    assistant.alive = False



def read_message(assistant, instance_vlc, player_vlc, username, password, sender_of_interest=None):
    imap = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    imap.login(username, password)
    imap.select('INBOX')
    if sender_of_interest is None:
        status, response = imap.search(None, '(UNSEEN)')
        unread_msg_nums = response[0].split()
    else:
        status, response = imap.search(None, '(UNSEEN)', '(FROM "%s")' % (sender_of_interest))
        unread_msg_nums = response[0].split()
    if unread_msg_nums:
        assistant.speak("Very good! Please wait, my assistant will read your messages!")
    else:
        assistant.speak("You do not have new messages!")
    for e_id in unread_msg_nums:
        _, header = imap.fetch(e_id, '(UID BODY[HEADER])')
        header = header[0][-1]
        header = "".join(header.split("\r"))
        header = [h for h in header.split("\n") if h != ""]
        subject = header[-1]
        sender = header[-3]
        _, text = imap.fetch(e_id, '(UID BODY[1])')
        text = text[0][1]
        text = "Content :"+text
        message = sender + ". " + subject + ". " + text
        read_nicely_text(message, instance_vlc, player_vlc)
    # Mark them as seen
    for e_id in unread_msg_nums:
        imap.store(e_id, '+FLAGS', '\Seen')
    


def send_message(assistant, username, password, receptor_of_interest):
    msg = MIMEMultipart()
 
    msg['From'] = username
    msg['To'] = receptor_of_interest
    msg['Subject'] = "SUBJECT OF THE EMAIL"
 
    body = "TEXT YOU WANT TO SEND"
     
    msg.attach(MIMEText(body, 'plain'))
     
    filename = "Functions.py"
    attachment = open(filename, "r")
 
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= " + filename)
     
    msg.attach(part)
 
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(username, password)
    text = msg.as_string()
    server.sendmail(username, receptor_of_interest, text)
    server.quit()

