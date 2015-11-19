from flask import Flask
from flask import jsonify
from pytube import YouTube
from xml.etree import ElementTree
import os
import sys
import cv2
import numpy

app = Flask(__name__)

@app.route("/fetch/<id>")
def process(id=None):
    # Download Video
    video_url = "https://www.youtube.com/watch?v=" + id
    video_id = downloadVideo(video_url, id)

    # Extract Video FRAMES
    frames = extractVideoFrames(video_id)


    return jsonify(num_frames = frames)

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

    number_frames = vidcap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
    print number_frames
    count = 0
    frame_count = 0
    frame_number = 1

    while (count < number_frames):
      frame_count += 1
      if (frame_count == 24):
          success,image = vidcap.retrieve()
          cv2.imwrite("/var/www/frames/" + video_id + "/%d.jpg" % frame_number, image)
          frame_count = 0;
          frame_number += 1;
      else:
          vidcap.grab()
      count += 1

    return frame_number


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int("8000"))
