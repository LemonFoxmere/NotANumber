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
    model.add(keras.layers.Dropout(0.4))
    model.add(keras.layers.Dense(30, activation = "relu"))
    model.add(keras.layers.Dropout(0.4))
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
    model.add(keras.layers.Dense(7*7*64, input_shape=(4,)))
    model.add(keras.layers.LeakyReLU())

    model.add(keras.layers.Dense(7*7*128))
    model.add(keras.layers.LeakyReLU())

    model.add(keras.layers.Dense(7*7*256))
    model.add(keras.layers.LeakyReLU())

    model.add(keras.layers.Reshape((7,7,256)))
    model.add(keras.layers.BatchNormalization())

    model.add(keras.layers.Convolution2DTranspose(128, (4,4), strides=(1,1), padding='same')) # 7 x 7 x 1 x 128
    model.add(keras.layers.BatchNormalization())
    model.add(keras.layers.LeakyReLU(0.3))

    model.add(keras.layers.Convolution2DTranspose(64, (4,4), strides=(2,2), padding='same')) # 14 x 14 x 1 x 64
    model.add(keras.layers.BatchNormalization())
    model.add(keras.layers.LeakyReLU(0.3))

    model.add(keras.layers.Convolution2DTranspose(32, (4,4), strides=(2,2), padding='same')) # 28 x 28 x 1 x 32
    model.add(keras.layers.BatchNormalization())
    model.add(keras.layers.LeakyReLU(0.3))

    model.add(keras.layers.Convolution2DTranspose(1, (2,2), strides=(1,1), padding='same', activation="tanh")) # 28 x 28 x 1 x 1

    return model

gen_model = make_generator_model()
gen_opt = Adam(learning_rate=lr)
gen_model.compile(gen_opt, "binary_crossentropy")

def get_gen_loss(gen_pred):
    gen_pred = gen_pred
    return tf.keras.losses.BinaryCrossentropy(from_logits=True)(tf.ones_like(gen_pred), gen_pred)

# generate input shape
def get_random_input(size, latent=np.array([None]), type="float32"):
    if(latent.any() == None): latent = np.random.randn(size, 2) # if no custom latent space defined

    new_col_1 = [(a+b)/2 for a,b in latent] # generate extra columns for ls
    new_col_2 = [(a*b) for a,b in latent]
    latent = np.insert(latent, latent.shape[1], new_col_1,axis=1)
    latent = np.insert(latent, 0, new_col_2,axis=1)

    return latent.astype("float32")

def train_step(images):
    gen_noise = get_random_input(BATCH_SIZE) # generate a random latent space vector and use that to train

    with tf.GradientTape() as gen_tape, tf.GradientTape() as disc_tape: # get grad tape
        generated_images = gen_model(gen_noise, training=True) # gen image from ls vector
        real_output = disc_model(images, training=True) # disc on real images
        fake_output = disc_model(generated_images, training=True) # disc on generated images

        gen_loss = get_gen_loss(fake_output) # generator loss
        disc_loss = get_disc_loss(real_output, fake_output) # discriminator loss

    # get gradients from gradient tape
    grad_gen = gen_tape.gradient(gen_loss, gen_model.trainable_variables)
    grad_disc = disc_tape.gradient(disc_loss, disc_model.trainable_variables)

    # apply gradients using optimizers
    gen_opt.apply_gradients(zip(grad_gen, gen_model.trainable_variables))
    disc_opt.apply_gradients(zip(grad_disc, disc_model.trainable_variables))

    # return losses w/ rounding
    return (round(np.mean(gen_loss),5), round(np.mean(disc_loss),5)) # current_gen_loss, current_disc_loss

# get a seed for progress monitoring. The seed will be a constant ls vector
seed = get_random_input(1)

def train(dataset, epochs):
    current_gen_loss = "N/A"
    current_disc_loss = "N/A"
    img_ct = 0
    ep = 0
    for i in range(epochs):
        ep+=1 # epoch tracking
        dataset_bar  = tqdm(dataset, bar_format='{l_bar}{bar:10}{r_bar}{bar:-10b}') # set tqdm bar description
        b=0 # current batch, used for animation purposes only
        for images in dataset_bar:
            dataset_bar.set_description(colored("Epoch: {s}/{t}".format(s=ep, t=epochs), 'white') +
                                        '; GenLoss:' + colored(str(current_gen_loss), 'grey', 'on_yellow') +
                                        '\t; DiscLoss:' + colored(str(current_disc_loss), 'grey', 'on_cyan') + '\t')
            images = tf.cast(images, tf.dtypes.float32)
            current_gen_loss, current_disc_loss = train_step(images)

            # UNCOMMENT THIS BLOCK IF YOU ARE TRYING TO MAKE ANIMATIONS
            # if(b%30 == 0): # save frame every 30 batches
            #     plt.imshow(tf.reshape(gen_model(seed, training=False), (28,28)), cmap="binary")
            #     plt.savefig('/home/lemonorange/GANnetworkTest/img/dcgan-2/frame'+str(img_ct),dpi=300)
            #     img_ct += 1
            # b += 1

        plt.imshow(tf.reshape(gen_model(seed, training=False), (28,28)), cmap="binary") # show training progression
        plt.show()

train(train_dataset,epoch) # train architecture

x = 2
y = -2
frames = -1
inc = 4/200 # interval / frame target



for i in tqdm(range(200)):
    with tf.device('/device:GPU:0'):
        lsi = get_random_input(1, latent=np.array([[x,y]]))

        x -= inc
        y += inc
        frames += 1

        result = gen_model.predict(lsi)
    plt.imshow(tf.reshape(result, (28,28)), cmap="binary")
    # plt.xlim(-1.5,1.5)
    # plt.ylim(-1.5,1.5)
    # plt.plot(x, y, 'o')
    # plt.savefig('img/dcgan-4-2/frame'+str(frames),dpi=300)
    plt.show()
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
