import os
import cv2
import time
import math
import shutil
import requests
import operator
import numpy as np
import matplotlib.pyplot as plt
from collections import namedtuple

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


def render_facedata_on_image(result, image):
    for face in result:
        rectangle = face["faceRectangle"]
        cv2.rectangle(
            image, (rectangle["left"], rectangle["top"]),
            (rectangle["left"] + rectangle["width"], rectangle["top"] + rectangle["height"]),
            color=(255, 0, 0), thickness=5)
        emotion = max(face["scores"].items(), key=operator.itemgetter(1))[0]
        textToWrite = "%s" % emotion
        cv2.putText(
            image, textToWrite,
            (rectangle["left"], rectangle["top"]-10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)


def analyze_web_image(image_url):
    headers = {
        "Ocp-Apim-Subscription-Key": _key,
        "Content-Type": "application/json"
    }
    json = {"url": image_url}
    result = process_request(json, None, headers, None)
    return result


def get_web_image(image_url):
    arr = np.asarray(bytearray(requests.get(image_url).content), dtype=np.uint8)
    image = cv2.cvtColor(cv2.imdecode(arr, -1), cv2.COLOR_BGR2RGB)
    return image


def analyze_disk_image(image_path):
    headers = {
        "Ocp-Apim-Subscription-Key": _key,
        "Content-Type": "application/octet-stream"
    }
    with open(image_path, "rb") as f:
        data = f.read()
    result = process_request(None, data, headers, None)
    return result


def get_disk_image(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    data8uint = np.fromstring(data, np.uint8)
    image = cv2.cvtColor(cv2.imdecode(data8uint, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
    return image


def get_sorted_emotions(single_face):
    return sorted(single_face["scores"].items(), key=operator.itemgetter(1), reverse=True)


def split_videos_into_frames(video_path, framedir, max_frames):
    print("capturing " + str(max_frames) + " frames...")
    if not os.path.exists(framedir):
        os.makedirs(framedir)
    cap = cv2.VideoCapture(video_path)
    framerate = cap.get(5)
    framecnt = 0
    while (cap.isOpened()):
        frameid = cap.get(1)
        ret, frame = cap.read()
        if not ret:
            break
        if frameid % math.floor(framerate) == 0:
            filename = framedir + "/frame_" + str(framecnt) + ".jpg"
            cv2.imwrite(filename, frame)
            framecnt += 1
            if framecnt == max_frames:
                break


def analyze_disk_video(video_path, frames):
    framedir = "frames"
    split_videos_into_frames(video_path, framedir, frames)

    print("sending images to Azure...")
    FrameData = namedtuple("FrameData", ["filename", "facedata", "image"])
    frameresults = []
    filenames = os.listdir(framedir)
    for i, filename in enumerate(filenames, start=1):
        relpath = framedir + "/" + filename
        print("sent %s/%s %s" % (i, len(filenames), filename))
        result = analyze_disk_image(relpath)
        image = get_disk_image(relpath)
        frameresults.append(FrameData(filename, result, image))

    print("deleting frames...")
    shutil.rmtree(framedir)

    print("done!")
    return frameresults


def show_facedata_on_image(facedata, image):
    render_facedata_on_image(facedata, image)
    plt.imshow(image)
    plt.show()
