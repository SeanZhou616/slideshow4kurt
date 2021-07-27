import cv2
import glob
import os
import numpy as np
import screeninfo
import random

pictures = ["jpg", "png", "jpeg"]
pictures = tuple(pictures)
videos = ["mp4", "mpeg", "avi"]
videos = tuple(videos)

WIDTH = 1920
HEIGHT = 1080
PIC_CYCLE = 20
PIC_DELAY = 1000
VIDEO_COVER_DELAY = 1000

import time
import vlc
from omxplayer.player import OMXPlayer
import dbus



def combine(img):
    height, width, _ = img.shape
    if width < height:
        width = int(width*HEIGHT/height)
        height = HEIGHT
        img = cv2.resize(img, (width, height))
        offset = WIDTH - width
        if offset > 0:
            bkgd_image = np.zeros((HEIGHT, offset//2, 3), np.uint8)
            combine_array = np.concatenate((bkgd_image, img), axis=1)
            combine_array = np.concatenate((combine_array, bkgd_image), axis=1)
            height, width, _ = combine_array.shape
            if width != WIDTH:
                offset_array = np.zeros((HEIGHT, 1, 3), np.uint8)
                combine_array = np.concatenate((combine_array, offset_array), axis=1)
        elif offset < 0:
            bkgd_image = np.zeros((HEIGHT, -offset//2, 3), np.uint8)
            combine_array = np.concatenate((bkgd_image, img), axis=1)
            combine_array = np.concatenate((combine_array, bkgd_image), axis=1)
            height, width, _ = combine_array.shape
            if width != WIDTH:
                offset_array = np.zeros((HEIGHT, 1, 3), np.uint8)
                combine_array = np.concatenate((combine_array, offset_array), axis=1)
        else:
            combine_array = img[:, :, :]
    else:
        height_temp = int(height*WIDTH/width)
        if height_temp > HEIGHT:
            width = int(width*HEIGHT/height)
            height = HEIGHT
            img = cv2.resize(img, (width, height))
            offset = WIDTH - width
            if offset > 0:
                bkgd_image = np.zeros((HEIGHT, offset//2, 3), np.uint8)
                combine_array = np.concatenate((bkgd_image, img), axis=1)
                combine_array = np.concatenate((combine_array, bkgd_image), axis=1)
                height, width, _ = combine_array.shape
                if width != WIDTH:
                    offset_array = np.zeros((HEIGHT, 1, 3), np.uint8)
                    combine_array = np.concatenate((combine_array, offset_array), axis=1)
            elif offset < 0:
                bkgd_image = np.zeros((HEIGHT, -offset//2, 3), np.uint8)
                combine_array = np.concatenate((bkgd_image, img), axis=1)
                combine_array = np.concatenate((combine_array, bkgd_image), axis=1)
                height, width, _ = combine_array.shape
                if width != WIDTH:
                    offset_array = np.zeros((HEIGHT, 1, 3), np.uint8)
                    combine_array = np.concatenate((combine_array, offset_array), axis=1)
            else:
                combine_array = img[:, :, :]
        else:
            height = height_temp
            width = WIDTH
            img = cv2.resize(img, (width, height))
            offset = HEIGHT - height
            if offset > 0:
                bkgd_image = np.zeros((offset//2, WIDTH, 3), np.uint8)
                combine_array = np.concatenate((bkgd_image, img), axis=0)
                combine_array = np.concatenate((combine_array, bkgd_image), axis=0)
                height, width, _ = combine_array.shape
                if height != HEIGHT:
                    offset_array = np.zeros((1, WIDTH, 3), np.uint8)
                    combine_array = np.concatenate((combine_array, offset_array), axis=0)
            elif offset < 0:
                bkgd_image = np.zeros((-offset//2, WIDTH, 3), np.uint8)
                combine_array = np.concatenate((bkgd_image, img), axis=0)
                combine_array = np.concatenate((combine_array, bkgd_image), axis=0)
                height, width, _ = combine_array.shape
                if height != HEIGHT:
                    offset_array = np.zeros((1, WIDTH, 3), np.uint8)
                    combine_array = np.concatenate((combine_array, offset_array), axis=0)
            else:
                combine_array = img[:, :, :]
    return combine_array

def process():
    screen = screeninfo.get_monitors()[0]
    path = "/media/pi/Pictures"
    counter = 0
    filenames_pics = []
    filenames_pics_display = []
    filenames_videos = []
    filenames_videos_display = []
    filename_last = ""
    
    for root, dirs, files in os.walk(path):
        for name in files:
            if name.endswith(pictures):
                filenames_pics.append(os.path.join(root, name))
                filenames_pics_display.append(name)
            elif name.endswith(videos):
                filenames_videos.append(os.path.join(root, name))
                filenames_videos_display.append(name)

    if len(filenames_pics) == 0 and len(filenames_videos) == 0:
        return

    prev_image = np.zeros((HEIGHT, WIDTH, 3), np.uint8)
    bkgd_image = np.zeros((HEIGHT, WIDTH, 3), np.uint8)
    while True:
        counter = counter + 1
        if counter < PIC_CYCLE + 1:
            choice = random.choice(list(enumerate(filenames_pics)))[0]
            filename = filenames_pics[choice]
            filename_display = filenames_pics_display[choice]
        else:
            choice = random.choice(list(enumerate(filenames_videos)))[0]
            filename = filenames_videos[choice]
            filename_display = filenames_videos_display[choice]
            counter = 0

        if filename == filename_last:
            continue
        if filename.endswith(pictures):
            print(filename)
            img = cv2.imread(filename)
            combine_array = combine(img)
            window_name = "Slideshow"
            cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
            cv2.moveWindow(window_name, screen.x - 1, screen.y - 1)
            cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

            for i in range(11):
                alpha = i/10
                beta = 1.0 - alpha
                length = len(filename_display)
                cv2.rectangle(combine_array, (0, 1030), (length * 25, 950), (0, 0, 0), -1)
                cv2.putText(combine_array, filename_display, (30, 1000), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                dst = cv2.addWeighted(combine_array, alpha, prev_image, beta, 0.0)                
                cv2.imshow(window_name, dst)
                if cv2.waitKey(1) == ord('q'):
                    return

            prev_image = combine_array

            if cv2.waitKey(PIC_DELAY) == ord('q'):
                return

        elif filename.endswith(videos):
            print(filename)
            cap = cv2.VideoCapture(filename)
            ret, img = cap.read()
            combine_array = combine(img)

            window_name = "Slideshow"
            cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
            cv2.moveWindow(window_name, screen.x - 1, screen.y - 1)
            cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            for i in range(11):
                alpha = i/10
                beta = 1.0 - alpha
                length = len(filename_display)
                cv2.rectangle(combine_array, (0, 1030), (length * 25, 950), (0, 0, 0), -1)
                cv2.putText(combine_array, filename_display, (30, 1000), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                dst = cv2.addWeighted(combine_array, alpha, prev_image, beta, 0.0)
                cv2.imshow(window_name, dst)
                if cv2.waitKey(1) == ord('q'):
                    return

            prev_image = combine_array
            if cv2.waitKey(VIDEO_COVER_DELAY) == ord('q'):
                return
            
           # player = OMXPlayer(filename,
           #         args="--win '0, 0, 1920, 1080'")
            player = OMXPlayer(filename)

            while not player.can_play():
                pass
            
            player.play_sync()

            time.sleep(1)
   
            cv2.imshow(window_name, combine_array)
            if cv2.waitKey(500) == ord('q'):
                    return
            cap.release()

        filename_last = filename
while True:
    try:
        process()

    except dbus.exceptions.DBusException:
        pass

    except KeyboardInterrupt:
        break
