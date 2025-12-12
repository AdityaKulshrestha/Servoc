from app.engine.model_loader import model


def model_inference(input_batch):
    return model.predict(input_batch)