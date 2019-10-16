from keras.models import load_model
import imageio
from os import listdir

models_folder = "/home/function/predict_api/"

def predict(input_image):
    models = [(load_model(models_folder + model, compile=False), model[:-15]) for model in listdir(models_folder) if model[-3:] == ".h5"]
    image = imageio.imread(input_image)
    image = image.reshape(1, image.shape[0], image.shape[1], image.shape[2])

    predictions = ["Prediction by model {}: {}".format(model[1], model[0].predict(image)[0][0]) for model in models]
    return predictions