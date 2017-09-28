import sys
import json
import requests
import operator
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
    "http://www.papajohns.com/a/img/content/pizza-family-img.jpg",
    "https://i.ytimg.com/vi/KTCQpjUrCe8/maxresdefault.jpg",
    "http://krnb.com/kj-midday/wp-content/uploads/sites/2/2014/03/sad-baby.jpg"
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


def get_emotions(face):
    """
    Args:
    (dict) face -- Azure data for a single face.

    Returns:
    (list: tuple) Emotions ordered by score.
    """
    return sorted(face["scores"].items(), key=operator.itemgetter(1), reverse=True)
