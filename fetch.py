import json
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

app = Flask(__name__)



@app.route("/fetch/<id>")
def process(id=None):
    # Download Video
    video_url = "https://www.youtube.com/watch?v=" + id
    video_id = downloadVideo(video_url, id)

    # Extract Video FRAMES
    total_frames, frames = extractVideoFrames(video_id)

    return jsonify(total_frames = total_frames, num_frames = frames, duration = get_duration(id))

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
    os.mkdir( path, 0755 )
    print "Directory Made"

    # Extract frames
    video_location = "/var/www/videos/" + video_id + ".mp4"
    vidcap = cv2.VideoCapture(video_location)

    number_frames = math.ceil(vidcap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
    print number_frames
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
