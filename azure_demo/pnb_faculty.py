"""
Example application applying Azure Emotion API to UConn Physiology and
Neurobiology Faculty 
"""

import os
import json
from collections import namedtuple
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from azure_demo import get_facedata


def get_local_file(filename):
    """
    Args:
    (str) filename -- File name located in current working directory.

    Returns:
    (str) Returns absolute path of local file.
    """
    return os.path.join(os.getcwd(), filename)

# File path for faculty data without emotions (before calling Azure).
FACULTY_RAW_DATA = get_local_file("pnb_faculty_raw.csv")

# File path for faculty data with emotions.
FACULTY_EMOTIONS_PATH = get_local_file("pnb_faculty_emotions.tsv")


class Faculty:
    """
    Represent faculty name, RateMyProfessor statistics, and url link to
    profile image. Emotion scores are initialized outside the
    constructor.
    """
    def __init__(self, name, rating, difficulty, url_image):
        """
        Attrs:
        (str) name -- Faculty name.
        (float) rating -- Ratemyprofessor overall rating.
        (float) difficulty -- Ratemyprofessor overall difficulty.
        (str) url_image -- URL string to image.
        (dict) emotions -- Emotion scores obtained from Azure.
        """
        self.name = name
        self.rating = rating
        self.difficulty = difficulty
        self.url_image = url_image
        self.emotions = None


def get_faculty():
    """
    Returns:
    (list: Faculty) Faculty objects parsed from PNB faculty CSV file.
    """
    data = []
    with open(FACULTY_RAW_DATA, "r") as f:
        for x in f.read().splitlines():
            d = x.split(",")
            if d[2] != "null" and d[3] != "null":
                data.append(Faculty(d[0], float(d[1]), float(d[2]), d[3]))
    return data


def add_emotions(faculty):
    """
    Retrieves emotion scores for all faculty profile images. Assumes
    that there is only one face in each profile image.

    Args:
    (list: Faculty) faculty -- Add emotion scores for all faculty
    members.
    """
    for x in faculty:
        print("emotionalize: %s" % x.name)
        x.emotions = json.dumps(get_facedata(x.url_image)[0]["scores"])


def output(faculty):
    """
    Ouptut faculty statistics and their emotion scores.

    Args:
    (list: Faculty) faculty -- List of all faculty objects.
    """
    with open(FACULTY_EMOTIONS_PATH, "w") as f:
        for x in faculty:
            f.write("%s\t%s\t%s\t%s\t%s\n" % (x.name, x.rating,
                x.difficulty, x.url_image, x.emotions))


def store_faculty_emotions():
    """
    Because Azure allows a limited number of API calls, store the
    faculty emotions and then do further processing.
    """
    faculty = get_faculty()
    add_emotions(faculty)
    output(faculty)


def get_faculty_emotions():
    """
    Returns:
    (list: Faculty) List of all faculty objects with emotions.
    """
    data = []
    with open(FACULTY_EMOTIONS_PATH, "r") as f:
        for x in f.read().splitlines():
            d = x.split("\t")
            faculty = Faculty(d[0], float(d[1]), float(d[2]), d[3])
            faculty.emotions = json.loads(d[4])
            data.append(faculty)
    return data


def plot_faculty_emotions():
    """
    Plot faculty rating, difficulty, and emotion in 3D.
    """
    faculty = get_faculty_emotions()
    fig = plt.figure()
    ax = Axes3D(fig)
    x_vals = [i.rating for i in faculty]
    y_vals = [i.difficulty for i in faculty]
    z_vals = [i.emotions["happiness"] for i in faculty]
    ax.scatter(x_vals, y_vals, z_vals)
    ax.set_title("happiness")
    ax.set_xlabel("rating (1-worst, 5-best)")
    ax.set_ylabel("difficulty (1-easy, 5-hard)")
    ax.set_zlabel("happiness")
    plt.show()


if __name__ == "__main__":
    print("analyzing faculty images...")
    store_faculty_emotions()

    print("plotting results...")
    plot_faculty_emotions()

    print("done!")