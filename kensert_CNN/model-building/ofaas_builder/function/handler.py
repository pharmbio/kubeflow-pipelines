from .predict_api import model_api as model

def handle(req):

    """handle a request to the function
    Args:
        req (str): request body
    """
    # write request as binary content to png image
    with open("img.png", "wb") as img_pointer:
        img_pointer.write(req)

    # predict on image file
    prediction = model.predict("img.png")
    return prediction
