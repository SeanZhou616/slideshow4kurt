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

import time
import vlc
import Xlib


class Player:
    '''
        args:设置 options
    '''
    def __init__(self, *args):
        if args:
            instance = vlc.Instance(*args)
            self.media = instance.media_player_new()
        else:
            self.media = vlc.MediaPlayer()

    # 设置待播放的url地址或本地文件路径，每次调用都会重新加载资源
    def set_uri(self, uri):
        self.media.set_mrl(uri)

    # 播放 成功返回0，失败返回-1
    def play(self, path=None):
        if path:
            self.set_uri(path)
            return self.media.play()
        else:
            return self.media.play()

    # 暂停
    def pause(self):
        self.media.pause()

    # 恢复
    def resume(self):
        self.media.set_pause(0)

    # 停止
    def stop(self):
        self.media.stop()

    # 释放资源
    def release(self):
        return self.media.release()

    # 是否正在播放
    def is_playing(self):
        return self.media.is_playing()

    # 已播放时间，返回毫秒值
    def get_time(self):
        return self.media.get_time()

    # 拖动指定的毫秒值处播放。成功返回0，失败返回-1 (需要注意，只有当前多媒体格式或流媒体协议支持才会生效)
    def set_time(self, ms):
        return self.media.get_time()

    # 音视频总长度，返回毫秒值
    def get_length(self):
        return self.media.get_length()

    # 获取当前音量（0~100）
    def get_volume(self):
        return self.media.audio_get_volume()

    # 设置音量（0~100）
    def set_volume(self, volume):
        return self.media.audio_set_volume(volume)

    # 返回当前状态：正在播放；暂停中；其他
    def get_state(self):
        state = self.media.get_state()
        if state == vlc.State.Playing:
            return 1
        elif state == vlc.State.Paused:
            return 0
        else:
            return -1

    # 当前播放进度情况。返回0.0~1.0之间的浮点数
    def get_position(self):
        return self.media.get_position()

    # 拖动当前进度，传入0.0~1.0之间的浮点数(需要注意，只有当前多媒体格式或流媒体协议支持才会生效)
    def set_position(self, float_val):
        return self.media.set_position(float_val)

    # 获取当前文件播放速率
    def get_rate(self):
        return self.media.get_rate()

    # 设置播放速率（如：1.2，表示加速1.2倍播放）
    def set_rate(self, rate):
        return self.media.set_rate(rate)

    # 设置宽高比率（如"16:9","4:3"）
    def set_ratio(self, ratio):
        self.media.video_set_scale(0)  # 必须设置为0，否则无法修改屏幕宽高
        self.media.video_set_aspect_ratio(ratio)

    # 注册监听器
    def add_callback(self, event_type, callback):
        self.media.event_manager().event_attach(event_type, callback)

    # 移除监听器
    def remove_callback(self, event_type, callback):
        self.media.event_manager().event_detach(event_type, callback)

    def fullscreen(self):
        self.media.toggle_fullscreen()

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
    filenames = []
    filenames_display = []
    filenames_pics = []
    filenames_pics_display = []
    filenames_videos = []
    filenames_videos_display = []
    filename_last = ""
    
    for root, dirs, files in os.walk(path):
        if files.endswith(pictures):
            filenames_pics.extend(os.path.join(root, names) for names in files)
            filenames_pics_display.extend(files)
        elif files.endswith(videos):
            filenames_videos.extend(os.path.join(root, names) for names in files)
            filenames_videos_display.extend(files)
        #filenames.extend(os.path.join(root, names) for names in files)
        #filenames_display.extend(files)
    if len(filenames_pics) == 0 and len(filenames_videos) == 0:
        return

    prev_image = np.zeros((HEIGHT, WIDTH, 3), np.uint8)
    bkgd_image = np.zeros((HEIGHT, WIDTH, 3), np.uint8)
    while True:
        counter = counter + 1
        if counter < 20:
            choice
        choice = random.choice(list(enumerate(filenames)))[0]
        filename = filenames[choice]
        filename_display = filenames_display[choice]
        if filename == filename_last:
            continue
        if filename.endswith(pictures):
            print(filename)
            img = cv2.imread(filename)
            combine_array = combine(img)

            for i in range(21):
                alpha = i/20
                beta = 1.0 - alpha
                length = len(filename_display)
                cv2.rectangle(combine_array, (0, 1030), (length * 20, 950), (0, 0, 0), -1)
                cv2.putText(combine_array, filename_display, (30, 1000), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                dst = cv2.addWeighted(combine_array, alpha, prev_image, beta, 0.0)
                

                window_name = "Slideshow"
                cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
                cv2.moveWindow(window_name, screen.x - 1, screen.y - 1)
                cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                cv2.imshow(window_name, dst)
                if cv2.waitKey(1) == ord('q'):
                    return

            prev_image = combine_array

            if cv2.waitKey(1000) == ord('q'):
                return

        elif filename.endswith(videos):
            print(filename)
            cap = cv2.VideoCapture(filename)
            ret, img = cap.read()
            combine_array = combine(img)

            for i in range(21):
                alpha = i/20
                beta = 1.0 - alpha
                length = len(filename_display)
                cv2.rectangle(combine_array, (0, 1030), (length * 20, 950), (0, 0, 0), -1)
                cv2.putText(combine_array, filename_display, (30, 1000), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                dst = cv2.addWeighted(combine_array, alpha, prev_image, beta, 0.0)
                

                window_name = "Slideshow"
                cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
                cv2.moveWindow(window_name, screen.x - 1, screen.y - 1)
                cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                cv2.imshow(window_name, dst)
                if cv2.waitKey(1) == ord('q'):
                    return

            if cv2.waitKey(1000) == ord('q'):
                return
            
            #Xlib.XInitThreads()
            #video_player = vlc.MediaPlayer(filename, "--no-xlib")
            video_player = Player("--no-xlib, --vebose=0")
            time.sleep(0.1)
            video_player.fullscreen()
            time.sleep(0.1)
            video_player.play(filename)
            time.sleep(0.1)
            while video_player.is_playing():
                time.sleep(0.5)
            cv2.imshow(window_name, combine_array)
            time.sleep(0.5)
            video_player.release()
            if cv2.waitKey(1) == ord('q'):
                    return
            # fps = int(round(cap.get(cv2.CAP_PROP_FPS)))
            # while cap.isOpened():
            #     ret, frame = cap.read()
            #     if ret:
            #         combine_array = combine(frame)
            #         cv2.imshow(window_name, combine_array)
            #         frame_last = frame
            #     else:
            #         prev_image = combine(frame_last)
            #         break
            #     k = cv2.waitKey(600//fps)
            #     if(k & 0xff == ord('q')):
            #         return
            cap.release()
            prev_image = dst

        filename_last = filename


process()
