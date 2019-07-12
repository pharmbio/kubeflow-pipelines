from keras.models import load_model
import imageio


def predict(input_image):
    model = load_model("/home/function/predict_api/saved_model.h5")
    image = imageio.imread(input_image)
    image = image.reshape(1, image.shape[0], image.shape[1], image.shape[2])

    prediction = "Prediction for input: {}".format(model.predict(image)[0][0])
    return prediction