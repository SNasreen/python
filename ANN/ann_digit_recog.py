# -*- coding: utf-8 -*-
"""ANN_digit_recog.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1gXsYJpPMy8oxC-Cn37SWibHiT0XEpHUP
"""

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras import layers
from tensorflow.keras.losses import SparseCategoricalCrossentropy

train = pd.read_csv("/train.csv")
X_test = pd.read_csv("/test.csv")

print("Dataset columns: ", train.columns)
print(train.info())

X = train.drop('label', axis = 1)
y = train.label

X = X / 255.0
X_test = X_test/255.0

X_train, X_val, y_train, y_val = train_test_split(X, y, train_size = 0.80, random_state = 42)

print(f"X_train shape: {X_train.shape}")
print(f"y_train shape: {y_train.shape}")

print(f"X_val shape: {X_val.shape}")
print(f"y_val shape: {y_val.shape}")

X_train_reshaped = X_train.values.reshape(-1, 28, 28)
plt.imshow(X_train_reshaped[0])

plt.figure(figsize=(10, 15))
for i in range(10):
    plt.subplot(5, 5, i+1)
    plt.grid(False)
    plt.imshow(X_train_reshaped[i])
    plt.xlabel(y_train.iloc[i])

input_shape = [X_train.shape[1]]

model_1 = Sequential([
    layers.BatchNormalization(input_shape=input_shape),
    Dense(units = 350, activation = 'relu'),
    layers.BatchNormalization(),
    layers.Dropout(0.3),

    Dense(units = 165, activation = 'relu'),
    layers.BatchNormalization(),
    layers.Dropout(0.3),

    Dense(units = 64, activation = 'relu'),
    layers.BatchNormalization(),
    layers.Dropout(0.3),
    Dense(units = 10, activation = 'linear')
])

model_2 = Sequential([
    layers.BatchNormalization(input_shape=input_shape),
    Dense(units = 80, activation = 'relu'),
    layers.BatchNormalization(),
    layers.Dropout(0.3),
    Dense(units = 10, activation = 'linear')
])

model_3 = Sequential([
    layers.BatchNormalization(input_shape=input_shape),
    Dense(units = 560, activation = 'relu'),
    layers.BatchNormalization(),
    layers.Dropout(0.3),
    Dense(units = 700, activation = 'relu'),
    layers.BatchNormalization(),
    layers.Dropout(0.3),

    Dense(units = 430, activation = 'relu'),
    layers.BatchNormalization(),
    layers.Dropout(0.3),

    Dense(units = 120, activation = 'relu'),
    layers.BatchNormalization(),
    layers.Dropout(0.3),

    Dense(units = 10, activation = 'linear')
])

models = [model_1, model_2, model_3]
nn_train_loss = []
nn_cv_loss    = []

early_stopping = keras.callbacks.EarlyStopping(
    patience=5,
    min_delta=0.001,
    restore_best_weights=True,
)

for model in models:
    model.compile(loss = SparseCategoricalCrossentropy(from_logits= True),
               optimizer = tf.keras.optimizers.Adam(learning_rate = 1e-3),
               metrics = ['accuracy'])

    print(f"Training model_{models.index(model) + 1}...")
    history = model.fit(X_train, y_train, epochs = 50,
           validation_data = (X_val, y_val),
                        batch_size = 50,
           callbacks=[early_stopping],
           verbose = 0
           )

    history_df = pd.DataFrame(history.history)
    history_df.loc[:, ['loss', 'val_loss']].plot(title="Cross-entropy")
    #history_df.loc[:, ['binary_accuracy', 'val_binary_accuracy']].plot(title="Accuracy")

    print("Done!\n")

# It's seems like model_1 performs better
best_model = model_1

# train on all the dataset
best_model.fit(X, y, callbacks=[early_stopping], batch_size = 50, epochs = 50)

#predict
test_predictions = tf.nn.softmax(best_model.predict(X_test)).numpy()

history_df = pd.DataFrame(history.history)
history_df.loc[:, ['loss', 'val_loss']].plot(title="Cross-entropy")
history_df.loc[:, ['accuracy', 'val_accuracy']].plot(title="Accuracy")

ImageId = []
Label = []
for i in range(len(test_predictions)):
    ImageId.append(i+1)
    Label.append(test_predictions[i].argmax())

submissions=pd.DataFrame({"ImageId": ImageId,
                         "Label": Label})
submissions.to_csv("submission.csv", index=False, header=True)