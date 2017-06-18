# -*- coding: utf-8 -*-
"""
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

chatbot = ChatBot("Ron Obvious")#read_only=True)

conversation = [
    "Hello",
    "Hi there!",
    "How are you doing?",
    "I'm doing great.",
    "That is good to hear",
    "Thank you.",
    "You're welcome."
]

chatbot.set_trainer(ListTrainer)
chatbot.train(conversation)

response = chatbot.get_response("Good morning!")
print(response)
"""


from chatterbot import ChatBot


# Enable info level logging
#logging.basicConfig(level=logging.INFO)

chatbot = ChatBot(
    'Example Bot',
    #trainer='chatterbot.trainers.UbuntuCorpusTrainer'
)

# Start by training our bot with the Ubuntu corpus data
chatbot.train()
print "training"
# Now let's get a response to a greeting
response = chatbot.get_response('How are you doing today?')
print(response)