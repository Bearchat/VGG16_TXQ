"""
mnist tester (train and test accuracy)

date: 9/24
author: arabian9ts
"""

# escape matplotlib error
import matplotlib
matplotlib.use('Agg')

# escape tensorflow warning
import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

import sys
import tensorflow as tf
import _pickle as pickle
import numpy as np
import datetime
import time
import matplotlib.pyplot as plt

from model.vgg16 import *
from util.util import *

# global variables
DATASET_NUM = 10000
BATCH = 64
EPOCH = 10

images = []
labels = []

def gen_onehot_list(label=0):
    """
    generate one-hot label-list based on ans-index
    e.g. if ans is 3, return [0, 0, 0, 1, 0, 0, 0, 0, 0, 0]

    Args: answer-index
    Returns: one-hot list
    """
    return [1 if l==label else 0 for l in range(0, 10)]    #注意其简洁的用法


def load_data():
    """
    open cifar-dataset
    segregate images-data and answers-label to images and labels
    """
    with open('dataset/data_batch_1', 'rb') as f:
        data = pickle.load(f, encoding='latin-1')
        slicer = int(DATASET_NUM*0.8)
        train_images = np.array(data['data'][:slicer]) / 255
        train_labels = np.array(data['labels'][:slicer])
        test_images = np.array(data['data'][slicer:]) / 255
        test_labels = np.array(data['labels'][slicer:])
        reshaped_train_images = np.array([x.reshape([32, 32, 3]) for x in train_images])
        reshaped_train_labels = np.array([gen_onehot_list(i) for i in train_labels])
        reshaped_test_images = np.array([x.reshape([32, 32, 3]) for x in test_images])
        reshaped_test_labels = np.array([gen_onehot_list(i) for i in test_labels])


    return reshaped_train_images, reshaped_train_labels, reshaped_test_images, reshaped_test_labels
        

def get_next_batch(max_length, length=BATCH, is_training=True):
    ##获取下一个minibatch，另一种方式
    """
    extract next batch-images

    Returns: batch sized BATCH
    """
    if is_training:
        indicies = np.random.choice(max_length, length)  #从0-（max_length-1）中随机以array形式返回length个数据
        #从np.arrary([max_length])中随机采样，返回length个采样点
        #可以从一个int数字或1维array里随机选取内容，并将选取结果放入n维array中返回。
        next_batch = train_images[indicies]
        next_labels = train_labels[indicies]
    else:
        indicies = np.random.choice(max_length, length)
        next_batch = test_images[indicies]
        next_labels = test_labels[indicies]

    return np.array(next_batch), np.array(next_labels)

def test():
    """
    do test
    """
    images, labels = get_next_batch(max_length=len(test_labels), length=100, is_training=False)
    result = sess.run(predict, feed_dict={input: images})

    correct = 0
    total = 100

    for i in range(len(labels)):
        pred_max = result[i].argmax()
        ans = labels[i].argmax()

        if ans == pred_max:
            correct += 1

    print('Accuracy: '+str(correct)+' / '+str(total)+' = '+str(correct/total))


with tf.Session() as sess:
    """
    TensorFlow session
    """
    args = sys.argv    #获取命令行参数  通过外部添加参数来决定是训练还是测试

    # use VGG16 network
    vgg = VGG16()       ###类的调用，构建实例
    # params for converting to answer-label-size
    w = tf.Variable(tf.truncated_normal([512, 10], 0.0, 1.0) * 0.01, name='w_last')
    b = tf.Variable(tf.truncated_normal([10], 0.0, 1.0) * 0.01, name='b_last')

    # input image's placeholder and output of VGG16
    input = tf.placeholder(shape=[None, 32, 32, 3], dtype=tf.float32)
    fmap = vgg.build(input, is_training=True)
    predict = tf.nn.softmax(tf.add(tf.matmul(fmap, w), b))  #归一化的向量

    # params for defining Loss-func and Training-step
    ans = tf.placeholder(shape=None, dtype=tf.float32)
    ans = tf.squeeze(tf.cast(ans, tf.float32))

    # cross-entropy
    loss = tf.reduce_mean(-tf.reduce_sum(ans * tf.log(predict), reduction_indices=[1]))
    optimizer = tf.train.GradientDescentOptimizer(0.05)
    train_step = optimizer.minimize(loss)

    sess.run(tf.global_variables_initializer())

    # load image data
    train_images, train_labels, test_images, test_labels = load_data()

    ### restoring saved parameters ###
    if 2 == len(args) and 'eval' == args[1]:
        # parameter saver
        saver = tf.train.Saver()
        saver.restore(sess, './params.ckpt')
        test()
        sys.exit()  #程序退出
    # ========= Loading END ======== #

    print('\nSTART LEARNING')
    print('==================== '+str(datetime.datetime.now())+' ====================')

    # Training-loop
    lossbox = []
    for e in range(EPOCH):
        for b in range(int(DATASET_NUM/BATCH)):
            batch, actuals = get_next_batch(len(train_labels))
            sess.run(train_step, feed_dict={input: batch, ans: actuals})

            print('Batch: %3d' % int(b+1)+', \tLoss: '+str(sess.run(loss, feed_dict={input: batch, ans: actuals})))

            if (b+1) % 100 == 0:
                print('============================================')
                print('START TEST')
                test()    #随时看数据防止过拟合
                print('END TEST')
                print('============================================')
            time.sleep(0)

        lossbox.append(sess.run(loss, feed_dict={input: batch, ans: actuals}))
        print('========== Epoch: '+str(e+1)+' END ==========')

    print('==================== '+str(datetime.datetime.now())+' ====================')
    print('\nEND LEARNING')

    # parameter saver
    saver = tf.train.Saver()
    saver.save(sess, './params.ckpt')

    # plot
    # plt.figure(1)
    plt.xlabel('Epoch1')
    plt.ylabel('Loss1')
    plt.plot(np.array(range(EPOCH)), lossbox)
    plt.show()
    # plt.show()
    
