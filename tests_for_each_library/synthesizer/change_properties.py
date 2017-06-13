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
engine.runAndWait()