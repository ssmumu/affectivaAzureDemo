import time
import requests
import operator

_url = "https://api.projectoxford.ai/emotion/v1.0/recognize"
_key = "edd4bbdd82bf459dac9fb5ecb60a6a37"
_maxNumRetries = 10


def process_request(json, data, headers, params):
    retries = 0
    result = None
    while True:
        response = requests.request("post", _url, json=json, data=data,
            headers=headers, params=params)
        if response.status_code == 429:
            print("Message: %s" % (response.json()["error"]["message"]))
            if retries <= _maxNumRetries:
                time.sleep(1)
                retries += 1
                continue
            else:
                print("Error: Failed after retrying!")
                break
        elif response.status_code == 200 or response.status_code == 201:
            if ("content-length" in response.headers
                    and int(response.headers["content-length"]) == 0):
                result = None
            elif ("content-type" in response.headers
                    and isinstance(response.headers["content-type"], str)):
                if ("application/json" in response.headers["content-type"].lower()):
                    result = response.json() if response.content else None
                elif "image" in response.headers["content-type"].lower():
                    result = response.content
        else:
            print("Error code: %d" % (response.status_code))
            print("Message: %s" % (response.json()["error"]["message"]))
        break
    return result


def analyze_web_image(image_url):
    headers = {
        "Ocp-Apim-Subscription-Key": _key,
        "Content-Type": "application/json"
    }
    json = {"url": image_url}
    result = process_request(json, None, headers, None)
    return result


def analyze_disk_image(image_path):
    headers = {
        "Ocp-Apim-Subscription-Key": _key,
        "Content-Type": "application/octet-stream"
    }
    with open(image_path, "rb") as f:
        data = f.read()
    result = process_request(None, data, headers, None)
    return result


def get_sorted_emotions(single_face):
    return sorted(single_face["scores"].items(), key=operator.itemgetter(1), reverse=True)
