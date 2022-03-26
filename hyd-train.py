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

BUFFER_SIZE = train_img.shape[0]
BATCH_SIZE = 100
train_dataset = tf.data.Dataset.from_tensor_slices(train_img).shuffle(BUFFER_SIZE).batch(BATCH_SIZE)

epoch = 10
lr = 1e-4
disc_lr = 1e-4

# disc model
def make_discriminator_model():
    model = keras.Sequential()
    model.add(keras.layers.Conv2D(32, (5,5), padding="same", input_shape=(28,28,1)))
    model.add(keras.layers.LeakyReLU())
    model.add(keras.layers.Dropout(0.3))

    model.add(keras.layers.Conv2D(16, (5,5), padding="same"))
    model.add(keras.layers.LeakyReLU())
    model.add(keras.layers.Dropout(0.3))

    model.add(keras.layers.Flatten())

    model.add(keras.layers.Dense(500, activation = "relu"))
    model.add(keras.layers.Dropout(0.3))
    model.add(keras.layers.Dense(100, activation = "relu"))
    model.add(keras.layers.Dropout(0.3))
    model.add(keras.layers.Dense(30, activation = "relu"))
    model.add(keras.layers.Dropout(0.3))
    model.add(keras.layers.Dense(1, activation = "softmax"))

    return model

disc_model = make_discriminator_model()
disc_model(np.random.rand(1,28,28,1).astype(np.float32)).numpy()
disc_opt = Adam(learning_rate=disc_lr)
disc_model.compile(disc_opt, "binary_crossentropy")

def get_disc_loss(real_pred, gen_pred):
    real_pred = real_pred
    gen_pred = gen_pred
    real_loss = tf.keras.losses.BinaryCrossentropy()(tf.ones_like(real_pred), real_pred)
    gen_loss = tf.keras.losses.BinaryCrossentropy()(tf.zeros_like(gen_pred), gen_pred)
    return real_loss + gen_loss

# generator
def make_generator_model():
    model = keras.Sequential()
    model.add(keras.layers.Dense(7*7*256, input_shape=(100,)))
    model.add(keras.layers.BatchNormalization())
    model.add(keras.layers.LeakyReLU(0.3))
    model.add(keras.layers.Reshape((7,7,256)))

    model.add(keras.layers.Convolution2DTranspose(128, (4,4), strides=(1,1), padding='same')) # 8 x 8 x 1 x 512
    model.add(keras.layers.BatchNormalization())
    model.add(keras.layers.LeakyReLU(0.3))

    model.add(keras.layers.Convolution2DTranspose(64, (4,4), strides=(2,2), padding='same')) # 8 x 8 x 1 x 512
    model.add(keras.layers.BatchNormalization())
    model.add(keras.layers.LeakyReLU(0.3))

    model.add(keras.layers.Convolution2DTranspose(32, (4,4), strides=(2,2), padding='same')) # 8 x 8 x 1 x 512
    model.add(keras.layers.BatchNormalization())
    model.add(keras.layers.LeakyReLU(0.3))

    model.add(keras.layers.Convolution2DTranspose(1, (2,2), strides=(1,1), padding='same', activation="tanh")) # 8 x 8 x 1 x 512

    return model

gen_model = make_generator_model()
gen_opt = Adam(learning_rate=lr)
gen_model.compile(gen_opt, "binary_crossentropy")

def get_gen_loss(gen_pred):
    gen_pred = gen_pred
    return tf.keras.losses.BinaryCrossentropy(from_logits=True)(tf.ones_like(gen_pred), gen_pred)

#train
seed = np.random.randn(1,100)
def train(dataset, epochs):
    current_gen_loss = "N/A"
    current_disc_loss = "N/A"
    img_ct = 0
    ep = 0
    for i in range(epochs):
        ep+=1
        dataset_bar  = tqdm(dataset, bar_format='{l_bar}{bar:10}{r_bar}{bar:-10b}')
        b=0
        for images in dataset_bar:
            dataset_bar.set_description(colored("Epoch: {s}/{t}".format(s=ep, t=epochs), 'white') +
                                        '; GenLoss:' + colored(str(current_gen_loss), 'grey', 'on_yellow') +
                                        '\t; DiscLoss:' + colored(str(current_disc_loss), 'grey', 'on_cyan') + '\t')
            images = tf.cast(images, tf.dtypes.float32)
            current_gen_loss, current_disc_loss = train_step(images)

            # if(b%30 == 0): # save image
            #     plt.imshow(tf.reshape(gen_model(seed, training=False), (28,28)), cmap="binary")
            #     plt.savefig('/home/lemonorange/GANnetworkTest/img/dcgan-2/frame'+str(img_ct),dpi=300)
            #     img_ct += 1
            # b += 1

        plt.imshow(tf.reshape(gen_model(seed, training=False), (28,28)), cmap="binary")
        plt.show()

def train_step(images):
    # images = np.random.rand(1,28,28,1).astype(np.float32)
    gen_noise = np.random.randn(BATCH_SIZE, 100).astype("float32")

    with tf.GradientTape() as gen_tape, tf.GradientTape() as disc_tape:
        generated_images = gen_model(gen_noise, training=True)
        real_output = disc_model(images, training=True)
        fake_output = disc_model(generated_images, training=True)

        gen_loss = get_gen_loss(fake_output)
        disc_loss = get_disc_loss(real_output, fake_output)

    grad_gen = gen_tape.gradient(gen_loss, gen_model.trainable_variables)
    grad_disc = disc_tape.gradient(disc_loss, disc_model.trainable_variables)

    gen_opt.apply_gradients(zip(grad_gen, gen_model.trainable_variables))
    disc_opt.apply_gradients(zip(grad_disc, disc_model.trainable_variables))

    return (round(np.mean(gen_loss),5), round(np.mean(disc_loss),5)) # current_gen_loss, current_disc_loss

train(train_dataset,epoch)

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

getsizeof(bytearray([123]))

# save the network
gen_model.save('networks/dcgan/dcgan-gen.h5')
disc_model.save('networks/dcgan/disc-gen.h5')

# save the whole output space to a latout file for storage
with open('raw/dcgan-out-imgs.json', 'w') as file:
    for i in range(128):
        for j in range(128):
            json.dump([255 for i in range(784)], file)














# prog end
