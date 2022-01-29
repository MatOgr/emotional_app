from .SER_model import create_callbacks, create_model, prepare_data


def train_model(train_data, val_data, model, _epochs=100, _callbacks=None):
    history = model.fit(
        train_data,
        epochs=_epochs,
        validation_data=val_data,
        callbacks=_callbacks
    )
    return history


if __name__ == "__main__":
    model = create_model()
    train_data, val_data = prepare_data()
    callbacks = create_callbacks()
    train_model(train_data, val_data, model, 100, callbacks)

    model.save('reko-model.h5')
