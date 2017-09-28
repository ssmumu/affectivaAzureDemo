import sys
import cv2
import json
import requests
import operator
import numpy as np
import matplotlib.pyplot as plt
import http.client
import urllib.parse
import urllib.request
import urllib.error
import base64

# Replace "OCP-Apim-Subscription-Key" with your API key.
HEADERS = {
    "Content-Type": "application/json",
    "Ocp-Apim-Subscription-Key": "edd4bbdd82bf459dac9fb5ecb60a6a37"
}

PARAMS = urllib.parse.urlencode({})

# Examples for happiness, anger, and fear.
EXAMPLES = [
    "http://cdn3-www.dogtime.com/assets/uploads/gallery/goldador-dog-breed-pictures/puppy-1.jpg",
    "https://i.ytimg.com/vi/KTCQpjUrCe8/maxresdefault.jpg",
    "http://krnb.com/kj-midday/wp-content/uploads/sites/2/2014/03/sad-baby.jpg",
    "http://www.papajohns.com/a/img/content/pizza-family-img.jpg"
]


def get_facedata(url_image):
    """
    Args:
    (str) url_image -- URL string to an image.

    Returns:
    (list: dict) Each element contains data for a single face in the
    image. Azure provides data for the position of the identified
    face and emotion scores.
    """
    con = http.client.HTTPSConnection("westus.api.cognitive.microsoft.com")
    con.request("POST", "/emotion/v1.0/recognize?%s"
        % PARAMS, "{'url': '%s'}" % url_image, HEADERS)
    facedata = json.loads(con.getresponse().read().decode("utf-8"))
    con.close()
    return facedata


def get_image(url_image):
    """
    Args:
    (str) url_image -- URL string to an image.

    Returns:
    (obj) Image object.
    """
    array = np.asarray(bytearray(requests.get(url_image).content), dtype=np.uint8)
    image = cv2.cvtColor(cv2.imdecode(array, -1), cv2.COLOR_BGR2RGB)
    return image

 
def apply_facedata_to_image(image, facedata):
    """
    Edit the image. Draw a rectangle around each face and show the
    emotion with the highest score.

    Args:
    (obj) image -- Image object.
    (list: dict) facedata -- Face data obtained from Azure.
    """
    for face in facedata:
        rectangle = face["faceRectangle"]
        emotion = max(face["scores"].items(), key=operator.itemgetter(1))[0]
        cv2.rectangle(
            image,
            (rectangle["left"], rectangle["top"]),
            (rectangle["left"] + rectangle["width"],
                rectangle["top"] + rectangle["height"]),
            color=(255, 0, 0), thickness=5)
        cv2.putText(
            image, emotion, 
            (rectangle["left"], rectangle["top"]-10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 1)


def show_image(image):
    """
    Show the image.

    Args:
    (obj) image -- Image object.
    """
    plt.imshow(image)
    plt.show()


def show_image_with_facedata(url_image, facedata):
    """
    Args:
    (str) url_image -- URL string to image.
    (list: dict) facedata -- Face data obtained from Azure.
    """
    image = get_image(url_image)
    apply_facedata_to_image(image, facedata)
    show_image(image)


def analyze(url_image):
    """
    Obtain data from Azure and show the results.

    Args:
    (str) url_image -- URL string to an image.
    """
    facedata = get_facedata(url_image)
    show_image_with_facedata(url_image, facedata)


if __name__ == "__main__":
    for url in EXAMPLES:
        analyze(url)
