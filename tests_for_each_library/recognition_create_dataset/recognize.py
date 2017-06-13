# -*- coding: utf-8 -*-
import sugartensor as tf
import numpy as np
import librosa
from model import *
import data
#sox -d recording.wav

#spell checker: http://norvig.com/spell-correct.html
#https://medium.com/@majortal/deep-spelling-9ffef96a24f6
#https://pypi.python.org/pypi/autocorrect/0.1.0
#https://www.kaggle.com/cpmpml/spell-checker-using-word2vec

#predict word  with W2V https://datascience.stackexchange.com/questions/9785/predicting-a-word-using-word2vec-model

#Conv NN
#https://adeshpande3.github.io/adeshpande3.github.io/A-Beginner's-Guide-To-Understanding-Convolutional-Neural-Networks/
#http://danielhnyk.cz/predicting-sequences-vectors-keras-using-rnn-lstm/

#CTC
#https://www.tensorflow.org/versions/r0.11/api_docs/python/nn/conectionist_temporal_classification__ctc_



import time

print time.time()

# set log level to debug
tf.sg_verbosity(10)

#
# hyper parameters
#

batch_size = 1     # batch size

#
# inputs
#

# vocabulary size
voca_size = data.voca_size

# mfcc feature of audio
x = tf.placeholder(dtype=tf.sg_floatx, shape=(batch_size, None, 20))

# sequence length except zero-padding
seq_len = tf.not_equal(x.sg_sum(axis=2), 0.).sg_int().sg_sum(axis=1)
print seq_len
print x

# encode audio feature
logit = get_logit(x, voca_size=voca_size)

# ctc decoding
decoded, _ = tf.nn.ctc_beam_search_decoder(logit.sg_transpose(perm=[1, 0, 2]), seq_len, merge_repeated=True)



# to dense tensor
y = tf.sparse_to_dense(decoded[0].indices, decoded[0].dense_shape, decoded[0].values) + 1

print time.time()
#
# regcognize wave file
#

# command line argument for input wave file path
#tf.sg_arg_def(file=('', 'speech wave file to recognize.'))

# load wave file
wav, _ = librosa.load("train.wav", mono=True, sr=16000)
# get mfcc feature
mfcc = np.transpose(np.expand_dims(librosa.feature.mfcc(wav, 16000), axis=0), [0, 2, 1])
#print mfcc
print time.time()
print librosa.feature.mfcc(wav, 16000).shape
print np.expand_dims(librosa.feature.mfcc(wav, 16000), axis=0).shape
print mfcc.shape
# run network
from autocorrect import spell

with tf.Session() as sess:

    # init variables
    tf.sg_init(sess)

    # restore parameters
    saver = tf.train.Saver()
    saver.restore(sess, tf.train.latest_checkpoint('asset/train'))
    # run session
    label = sess.run(y, feed_dict={x: mfcc})

    # print label
    data.print_index(label)
    print label
    txt = data.index2str(label[0])
    for w in txt.split():
        print spell(w)
    print time.time()
