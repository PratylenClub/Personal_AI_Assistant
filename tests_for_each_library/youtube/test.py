import urllibimport urllib2from bs4 import BeautifulSoupfrom __future__ import unicode_literalsimport youtube_dltextToSearch = 'hello world'query = urllib.quote(textToSearch)url = "https://www.youtube.com/results?search_query=" + queryresponse = urllib2.urlopen(url)html = response.read()soup = BeautifulSoup(html)for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):    print 'https://www.youtube.com' + vid['href']ydl_opts = {    'format': 'bestaudio/best',    'postprocessors': [{        'key': 'FFmpegExtractAudio',        'preferredcodec': 'mp3',        'preferredquality': '192',    }],}with youtube_dl.YoutubeDL(ydl_opts) as ydl:    ydl.download(['http://www.youtube.com/watch?v=BaW_jenozKc'])