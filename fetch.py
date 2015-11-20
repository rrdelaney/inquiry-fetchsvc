from isodate import parse_duration as _
from urllib2 import urlopen
from flask import Flask, jsonify
from pytube import YouTube
from xml.etree import ElementTree

import os
import sys
import cv2
import numpy
import math
import json
import subprocess
import re


app = Flask(__name__)

# Get video captions
@app.route("/captions/<id>")
def process_captions(id=None):
    video_url = "https://www.youtube.com/watch?v=" + id
    # navigate to /var/www/cations/<id>
    path = "/var/www/captions"
    os.chdir(path)
    # get captions in srt
    f = os.popen("youtube-dl --list-subs --skip-download --output " + "'" + id + ".%(ext)s' " + video_url)
    info = f.read()
    searchObj = re.search(r'(no subtitles)', info, re.M|re.I)
    if searchObj:
        return jsonify(downloaded = False)
    else:
        os.system("youtube-dl --write-srt --sub-lang en --skip-download --output " + "'" + id + ".%(ext)s' " + video_url)
        return jsonify(downloaded = True)


# Process video
@app.route("/fetch/<id>")
def process(id=None):
    # Download Video
    video_url = "https://www.youtube.com/watch?v=" + id
    video_id = downloadVideo(video_url, id)
    # Extract Video FRAMES
    total_frames, frames = extractVideoFrames(video_id)
    d = get_duration(id)
    d = d - 1
    return jsonify(total_frames = total_frames, num_frames = frames, duration = d)

def get_duration(id):
    """ Get Youtube video duration for a video """
    raw_data = urlopen("https://www.googleapis.com/youtube/v3/videos?id=" + id + "&key=AIzaSyAYsu0030jO6YPDHChQyh7xKX9mSRR1Tto&part=contentDetails").read()
    json_data = json.loads(raw_data)
    return _(json_data['items'][0]['contentDetails']['duration']).total_seconds()


def downloadVideo(video_url, video_id):
    yt = YouTube(video_url)
    yt.set_filename(video_id)
    video = yt.get('mp4', '720p')
    video.download('/var/www/videos')
    return yt.filename

def extractVideoFrames(video_id):
    # make directory
    path = "/var/www/frames/" + video_id

    try:
        os.mkdir(path)
    except OSError as error:
        print "EXCEPTION RAISED: " + error
        return error
    else:
        print "DIRECTORY MADE"

    # Extract frames
    video_location = "/var/www/videos/" + video_id + ".mp4"
    vidcap = cv2.VideoCapture(video_location)

    number_frames = math.ceil(vidcap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
    count = 0
    frame_count = 0
    frame_number = 1

    while (count < number_frames):
      frame_count += 1
      if (frame_count == 24):
          success,image = vidcap.read()
          cv2.imwrite("/var/www/frames/" + video_id + "/%d.jpg" % frame_number, image)
          frame_count = 0;
          frame_number += 1;
      else:
          vidcap.grab()
      count += 1

    return number_frames, frame_number - 1


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int("8000"))
