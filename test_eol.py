azaze
fqzed
zEze
from scipy.spatial.distance import cosine
from random import choice
import shelve
import speech_recognition as sr
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize,sent_tokenize
from collections import Counter
from numpy import unique,log,asarray
from numpy.random import random
import gensim
import fileinput

TIME_OUT_CONSTANT = 5
PHRASE_TIME_LIMIT = 10
CENTROID = "centroid"
WEIGHT = "weight"
DF = "DF"
TF = "TF"
TF_IDF = "TF_IDF"
D = "D"
STOP_WORD = "stop_word"
SPEECH_RECOGNITION = "speech_recognition"
TRIGGER_SENTENCES = "Trigger sentences"
ACTION = "Action"
PARAMETERS = "Parameters"
ENGLISH = "english"
SINGLE = "single"
AVERAGE = "average"


class personal_assistant:
    def __init__(self,
        word2vec_model_path,
        pyttx_engine,
        speech_recognition_microphone,
        speech_recognizer,
        actions_dict,
        trigger_dict,
        confirmation_threshold,
        tf_idf_shelve_file_name,
        w2v_huge_model_path,
        language = ENGLISH,
        comparison_method = SINGLE,
        w2v_binary = False,
        ):
        """
        This class creates a simple personal assistant
        :param word2vec_model_path: Word2Vect gensim model path format bin
        :param pyttx_engine: pyttx voice synthesizer engine 
        :param speech_recognition_microphone: microphone engine from speech recognition library
        :param speech_recognizer: Speech recognizer engine from speech recognizer library
        :param actions_dict: Dictionary of actions. Each entry corresponds to a possible action. The key is the name of the action, and the value is another dictionary with the following format: {"Parameters": tuple or dictionary of other possible parameters required for the action, "Action": Function}
        :param trigger_dict: Dictionary of triggers. Each entry corresponds to a possible action. The key is the name of the action, and the value is a string containing each a possible trigger sentence.
        :param confirmation_threshold: Distance threshold between order and action beyond which the assistent ask for a confirmation
        :param tf_idf_shelve_file_name: File name for a shelve containing the Term Frequency dictionary associated to each action, the Inverse Document Frequency for each word, the TF-IDF for each word in each action and the centroid of each action
        :param language: String containing the language used
        """
        self.w2v_model_path = word2vec_model_path
        self.w2v_binary = w2v_binary
        print "loading brain"
        self.w2v_model = gensim.models.KeyedVectors.load_word2vec_format(self.w2v_model_path,binary=self.w2v_binary)#"Wikipedia_Simple_W2V_model.bin",binary=False)
        print "brain loaded"
        self.pyttx_voice = pyttx_engine
        self.sr_mic = speech_recognition_microphone
        self.sr_recognizer = speech_recognizer
        self.actions_dict = actions_dict
        self.trigger_dict = trigger_dict
        self.confirmation_threshold = confirmation_threshold
        self.tf_idf_shelve_file_name = tf_idf_shelve_file_name
        self.alive = True
        self.language = language
        self.w2v_huge_model_path = w2v_huge_model_path
        self.stopwords = set(stopwords.words(language))
        self.comparison_method = comparison_method
        self.fill_tf_idf_shelve()

    def tokenize_text(self,txt):
        tokenized_txt = word_tokenize(txt)
        tokenized_txt = [word.lower() for word in tokenized_txt if word.isalnum() and word not in self.stopwords]
        return tokenized_txt
        
    def fill_tf_idf_shelve(self):
        tf_idf_shelve = shelve.open(self.tf_idf_shelve_file_name, writeback=True)
        if TF not in tf_idf_shelve:
            tf_idf_shelve[TF] = {}
        if DF not in tf_idf_shelve:
            tf_idf_shelve[DF] = {}
        if D not in tf_idf_shelve:
            tf_idf_shelve[D] = 0
        if TF_IDF not in tf_idf_shelve:
            tf_idf_shelve[TF_IDF] = {}
        if CENTROID not in tf_idf_shelve:
            tf_idf_shelve[CENTROID] = {}

        for action,trigger_txt in self.trigger_dict.iteritems():
            if action not in tf_idf_shelve[TF].keys():
                trigger = self.tokenize_text(trigger_txt)
                tf_idf_shelve[TF][action] = Counter(trigger)
                for word in unique(trigger):
                    if word not in tf_idf_shelve[DF].keys():
                        tf_idf_shelve[DF][word] = 0
                    tf_idf_shelve[DF][word] += 1
        tf_idf_shelve[D] = len(tf_idf_shelve[TF])
        tf_idf_shelve.close()
        self.compute_tf_idf()
        self.compute_centroids()

    def compute_tf_idf(self):
        tf_idf_shelve = shelve.open(self.tf_idf_shelve_file_name, writeback=True)
        for action in tf_idf_shelve[TF].keys():
            if action not in tf_idf_shelve[TF_IDF]:
                tf_idf_shelve[TF_IDF][action] = {}
            for word,df in tf_idf_shelve[TF][action].iteritems():
                tf_idf_shelve[TF_IDF][action][word] = df * log(tf_idf_shelve[D] * 1. / tf_idf_shelve[DF][word])
        tf_idf_shelve.close()

    def compute_action_centroid(self,action):
        tf_idf_shelve = shelve.open(self.tf_idf_shelve_file_name,writeback=True)
        words = tf_idf_shelve[TF_IDF][action].keys()
        self.learn_words(words)
        tf_idf_words = asarray([tf_idf_shelve[TF_IDF][action][word] for word in words])
        tf_idf_words = tf_idf_words.reshape(tf_idf_words.size,1)
        centroid = (self.w2v_model[words] * tf_idf_words).sum(0) * 1./tf_idf_words.sum()
        tf_idf_shelve[CENTROID][action] = centroid
        tf_idf_shelve.close()

    def learn_words(self,words):
        unknown_words = set([word for word in words if word not in self.w2v_model.vocab])
        nb_words_to_add = len(unknown_words)
        self.add_list_of_words_in_w2v_model(unknown_words)
        if nb_words_to_add:
            self.update_nb_words_in_w2v_model(nb_words_to_add)
            self.w2v_model = gensim.models.KeyedVectors.load_word2vec_format(self.w2v_model_path,binary=self.w2v_binary)

    def add_list_of_words_in_w2v_model(self, unknown_words):
        huge_w2v_model_file = open(self.w2v_huge_model_path, "r")
        current_w2v_model_file = open(self.w2v_model_path, "a")
        line = huge_w2v_model_file.readline()
        unknown_words_left = len(unknown_words)
        while line and unknown_words_left:
            word = line.split()[0]
            if word in unknown_words:
                current_w2v_model_file.write(line)
                unknown_words = unknown_words - set([word])
                unknown_words_left -= 1
            line = huge_w2v_model_file.readline()
        for word in list(unknown_words):
            random_position = random(self.w2v_model.vector_size)*2-1
            current_w2v_model_file.write(" ".join(([word]+[str(x) for x in random_position])))
            print "warning random positions introduced for new words ... in the future this should be solved"
        current_w2v_model_file.close()
        huge_w2v_model_file.close()

    
    def update_nb_words_in_w2v_model(self, nb_words_to_add):
        current_w2v_model_file = open(self.w2v_model_path, "r+")
        future_nb_words = len(self.w2v_model.vocab) + nb_words_to_add
        current_w2v_model_file.write(str(future_nb_words)+" "+str(self.w2v_model.vector_size))
        current_w2v_model_file.close()

    def compute_centroids(self):
        tf_idf_shelve = shelve.open(self.tf_idf_shelve_file_name, writeback=True)
        list_of_actions = tf_idf_shelve[TF_IDF].keys()
        tf_idf_shelve.close()
        for action in list_of_actions:
            self.compute_action_centroid(action) 

    def learn_sentence(self,action,list_of_words):
        tf_idf_shelve = shelve.open(self.tf_idf_shelve_file_name,writeback=True)
        for word in list_of_words:
            if word not in tf_idf_shelve[TF][action]:
                tf_idf_shelve[TF][action][word] = 0
                if word not in tf_idf_shelve[DF]:
                    tf_idf_shelve[DF][word] = 0    
                tf_idf_shelve[DF][word] += 1
            tf_idf_shelve[TF][action][word] += 1
        tf_idf_shelve.close()
        self.compute_tf_idf()
        self.compute_centroids()

    def compute_list_of_words_centroid(self, words):
        self.learn_words(words)
        tf_idf_shelve = shelve.open(self.tf_idf_shelve_file_name,writeback=True)
        tf_idf_words = log((tf_idf_shelve[D] + 1) * 1./(asarray([tf_idf_shelve[DF][word] if word in tf_idf_shelve[DF].keys() else 0 for word in words]) + 1))
        tf_idf_words = tf_idf_words.reshape(tf_idf_words.size, 1)
        print words
        centroid = (self.w2v_model[words] * tf_idf_words).sum(0) * 1./tf_idf_words.sum()
        tf_idf_shelve.close()
        return centroid   

    def choose_best_action(self, list_of_words):
        min_distance = 3
        best_matching_action = None
        tf_idf_shelve = shelve.open(self.tf_idf_shelve_file_name)
        current_sentence_centroid = self.compute_list_of_words_centroid(list_of_words)
        for action,centroid in tf_idf_shelve[CENTROID].iteritems():
            distance = cosine(centroid,current_sentence_centroid)
            print action,distance
            if distance <= min_distance:
                min_distance = distance
                best_matching_action = action
        tf_idf_shelve.close()
        return current_sentence_centroid, best_matching_action, min_distance

    def active_listen(self):
        with self.sr_mic() as microphone:
            try:
                audio = self.sr_recognizer.listen(microphone,timeout=TIME_OUT_CONSTANT, phrase_time_limit=PHRASE_TIME_LIMIT)
            except sr.WaitTimeoutError:
                pass
        msg = ""
        try:
            msg = self.sr_recognizer.recognize_google(audio)#,language="fr-FR") 
            #msg = self.sr_recognizer.recognize_sphinx(audio)
            print(msg.lower())
        except sr.UnknownValueError:
            pass#print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            self.speak("Could not request results from Google STT. Check your connection! {0}".format(e))
        except:
            pass#self.speak("Something it is Wrong! It hurts! Wrong! Wrong! Wrong!")
        finally:
            return msg.lower()

    def speak(self,text):
        self.pyttx_voice.say(text)
        self.pyttx_voice.runAndWait()


    def ask_confirmation(self,best_matching_action):
        alternative_formulations = sent_tokenize(self.trigger_dict[best_matching_action])
        alternative_formulation = choice(alternative_formulations)
        self.speak("Excuse me, I didn't understand your request very well. Do you want me to "+alternative_formulation)
        answer = self.active_listen()
        if "no" in answer:
            self.speak("Please reformulate your request.")
            return 0
        if "yes" in answer:
            self.speak("Very good")
            return 1

    def execute_action(self,action):
        parameters = self.actions_dict[action][PARAMETERS]
        function = self.actions_dict[action][ACTION]
        if isinstance(parameters, tuple):
            function(self,*parameters)
        if isinstance(parameters, dict):
            function(self,**parameters)
        print parameters,function

    def interactive_step(self):
        msg = self.active_listen()
        print msg
        if not msg:
            return 0
        words = self.tokenize_text(msg)
        if not words:
            return 0
        current_sentence_centroid, best_matching_action, min_distance = self.choose_best_action(words)
        print "best action found " + best_matching_action
        #print current_sentence_centroid, best_matching_action, min_distance
        if min_distance >= self.confirmation_threshold:
            confirmation = self.ask_confirmation(best_matching_action)
            if not confirmation:
                return 0
        self.learn_sentence(best_matching_action, words)
        self.execute_action(best_matching_action)
        return 1

    def interactive_loop(self):
        while self.alive:
            self.interactive_step()