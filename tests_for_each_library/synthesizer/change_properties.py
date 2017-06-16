import pyttsx
engine = pyttsx.init()
voices = engine.getProperty('voices')
print voices
for voice in voices:
    if voice.languages[0] == u'en-US':
        print voice.id
        engine.setProperty('voice', voice.id)
        engine.say('The quick brown fox jumped over the lazy dog.')
        print voice.languages
    """
    if voice.languages[0] == u'es-ES':
        print voice.id
        engine.setProperty('voice', voice.id)
        engine.say('El rapido zorro salto sobre el flojo perro.')
        print voice.languages
    if voice.languages[0] == u'fr-FR':
        print voice.id
        engine.setProperty('voice', voice.id)
        engine.say('Le rapide renard sauta sur le chien paraisseux.')
        print voice.languages
    else:
        print "other",voice.languages,voice.id
    """
engine = pyttsx.init()
rate = engine.getProperty('rate')
engine.setProperty('rate', rate+50)
engine.say('The quick brown fox jumped over the lazy dog.')
engine.runAndWait()

engine = pyttsx.init()
volume = engine.getProperty('volume')
engine.setProperty('volume', volume-0.25)
engine.say('The quick brown fox jumped over the lazy dog.')
engine.runAndWait()

#http://pyttsx.readthedocs.io/en/latest/engine.html