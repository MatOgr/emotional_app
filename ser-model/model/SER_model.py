import keras
from keras.models import Sequential
from keras.callbacks import ReduceLROnPlateau
from keras.preprocessing.image_dataset import image_dataset_from_directory
from keras.layers import Conv2D, Dense, MaxPooling2D, Flatten, Dropout, BatchNormalization, RandomZoom, RandomFlip, RandomHeight, RandomWidth


def create_model(with_augment=False):
    """Creates the model based on concept from 'FSER: Deep Convolutional Neural Networks for Speech Emotion Recognition' by Bonaventure F. P. Dossou and Yeno K. S. Gbenou

    Args:
        with_augment (bool, optional): determining whther to use augmentation of images or not. Defaults to False.

    Returns:
        tf.keras.Sequential: model prepared to build and 
    """
    model = Sequential()

    if with_augment:
        model.add(RandomWidth((-0.2, 0.2)))
        model.add(RandomHeight((-0.2, 0.2)))
        model.add(RandomZoom(0.2))  # normally turned on
        model.add(RandomFlip("horizontal"))  # normally turned on

    model.add(Conv2D(
        filters=8,
        kernel_size=(5, 5),
        padding='same',
        activation='relu'
    ))
    model.add(MaxPooling2D(
        pool_size=(2, 2),
        padding='same'
    ))
    model.add(Dropout(0.2))

    model.add(Conv2D(
        filters=16,
        kernel_size=(5, 5),
        padding='same',
        activation='relu'
    ))
    model.add(MaxPooling2D(
        pool_size=(2, 2),
        padding='same'
    ))
    model.add(Dropout(0.2))

    model.add(Conv2D(
        filters=100,
        kernel_size=(5, 5),
        padding='same',
        activation='relu'
    ))
    model.add(MaxPooling2D(
        pool_size=(2, 2),
        padding='same'
    ))
    model.add(Dropout(0.2))

    model.add(Conv2D(
        filters=200,
        kernel_size=(5, 5),
        padding='same',
        activation='relu'
    ))
    model.add(MaxPooling2D(
        pool_size=(2, 2),
        padding='same'
    ))
    model.add(Dropout(0.2))

    model.add(Flatten())
    model.add(Dense(units=17424))
    model.add(Dense(units=1024))
    model.add(BatchNormalization())
    model.add(Dense(units=500))
    model.add(Dense(units=8, activation='softmax'))

    model.compile(
        optimizer='SGD',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    return model


def create_callbacks(_monitor='loss', _factor=0.4, _verbose=0, _patience=2, _min_lr=0.000001):
    """Creates ReduceLROnPlateau callback, reducing learning rate when a metric stops improving

    Args:
        _monitor (str, optional): monitor value. Defaults to 'loss'.
        _factor (float, optional): factor reducing the learning rate. next_lr = lr * factor. Defaults to 0.4.
        _verbose (int, optional): updating info - 1: update, 0: quiet. Defaults to 0.
        _patience (int, optional): number of no-improvement epochs to wait until learning rate reduction. Defaults to 2.
        _min_lr (float, optional): minimum value of learning rate. Defaults to 0.000001.

    Returns:
        tf.keras.callbacks.ReduceLROnPlateau: callback function to provide for model training
    """
    rlrp = ReduceLROnPlateau(
        monitor=_monitor,
        factor=_factor,
        verbose=_verbose,
        patience=_patience,
        min_lr=_min_lr
    )
    return rlrp


def prepare_data(path_to_data='data/train', path_to_val=None, _validation_split=0.2, _seed=1337, _image_size=(64, 64), _batch_size=64):
    """Creates tensorflow Datasets binded to given path - assumes, that folders containing data preserves keras dataset folders structure

    Args:
    -------
        path_to_data (str, optional): path to root folder of dataset (path has to be relative to the position of script compilation). Defaults to 'data'.
        path_to_val (str, optional): Seperate path to validation set root folder. Defaults to None.
        _validation_split (float, optional): Percent of data used for validation set. Ignored, while 'path_to_val' provided. Defaults to 0.2.
        _seed (int, optional): seed value for random samples generation. Defaults to 1337.
        _image_size (tuple, optional): size of images to be used in a dataset. Defaults to (64, 64).
        _batch_size (int, optional): batch size to be used in training. Defaults to 64.

    Returns:
    ---------
        tuple(tf.data.Dataset): tuple containing both training and validation (in that order)
    """
    train_data = image_dataset_from_directory(
        path_to_data,
        validation_split=_validation_split if not path_to_val else None,
        subset='training' if not path_to_val else None,
        seed=_seed if not path_to_val else None,
        image_size=_image_size,
        batch_size=_batch_size
    )
    validation_data = image_dataset_from_directory(
        path_to_val or path_to_data,
        validation_split=_validation_split if not path_to_val else None,
        subset='validation' if not path_to_val else None,
        seed=_seed if not path_to_val else None,
        image_size=_image_size,
        batch_size=_batch_size
    )
    return train_data, validation_data
