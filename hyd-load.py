# WARNING: this is NOT a regular python file!!! I used hydrogen when working with this python file, so it acts more as a jupyter notebook more than anything

import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras.optimizers import Adam, SGD, RMSprop
import numpy as np
import time
import keras
from tqdm import tqdm
import random
from termcolor import colored
import time
from PIL import Image
from sys import getsizeof
import json

from tensorflow.python.client import device_lib

def get_available_gpus():
    local_device_protos = device_lib.list_local_devices()
    return [x.name for x in local_device_protos if x.device_type == 'GPU']

get_available_gpus()

physical_devices = tf.config.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], False)

(train_img, train_lbl), (test_img, test_lbl) = tf.keras.datasets.mnist.load_data()
plt.imshow(train_img[random.randint(0,1000)], cmap="binary")
train_img = train_img.reshape(train_img.shape[0], 28, 28, 1)

train_img = (train_img - 127.5)/127.5 # normalize from -1 to 1

gen_model = keras.models.load_model("networks/dcgan/dcgan-gen.h5")
disc_model = keras.models.load_model("networks/dcgan/dcgan-disc.h5")

x = 0
y = 0
inc = 0.1
frames = -1

for i in tqdm(range(1200)):
    with tf.device('/device:GPU:0'):
        latent = [np.cos(x * (i-61*y)/25) + np.sin(y * (i-86*x)/25) for i in range(100)]
        np_latent = np.array(latent)

        inc += 0.004
        x = 1*np.sin(inc * 2.3 + 75)
        y = 1*np.cos(inc * 1.2)

        frames += 1

        result = gen_model.predict(np_latent.reshape((1,100)))
    plt.imshow(tf.reshape(result, (28,28)), cmap="binary")
    # plt.xlim(-1.5,1.5)
    # plt.ylim(-1.5,1.5)
    # plt.plot(x, y, 'o')
    plt.savefig('img/dcgan-4-2/frame'+str(frames),dpi=300)
    # plt.show()
    plt.cla()

plt.imshow(tf.reshape(gen_model(np.random.randn(1,100)), (28,28)), cmap="binary")

np.max(gen_model(np.random.randn(1,100)))

# save the whole output space to a latout file for storage
with open('raw/dcgan-out.json', 'w') as file:
    for i in range(128):
        for j in range(128):
            json.dump([255 for i in range(784)], file)














# prog end
