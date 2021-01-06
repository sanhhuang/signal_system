# _*_ coding: utf-8 _*_

import os
from numpy.lib.function_base import _select_dispatcher
import pyaudio
import threading
import wave
import time
import matplotlib.pyplot as plt
import numpy as np
import copy
from datetime import datetime
from processaudio import *
from denoise import *

class Recorder:
    def __init__(self, chunk=1024, channels=2, rate=44100, is_save=True):
        self.CHUNK = chunk
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = channels
        self.RATE = rate
        self._is_save = is_save
        self._running = False
        self._frames = []
        self._origin_data = b''
        self._read_queue_max_size = 2
        self._read_queue = []

    def findInternalRecordingDevice(self, p):
        # 要找查的设备名称中的关键字
        targetName = "Microsoft"
        targetType = "Input"
        for i in range(p.get_device_count()):
            devInfo = p.get_device_info_by_index(i)
            if (
                devInfo["name"].find(targetName) >= 0
                and devInfo["name"].find(targetType) >= 0
                and devInfo["hostApi"] == 0
            ):
                print(devInfo)
                return i
        print("ERR: Cannot find RecordDevice!")
        return -1

    def showInternalRecordingDevice(self, p):
        for i in range(p.get_device_count()):
            devInfo = p.get_device_info_by_index(i)
            print(devInfo)

    # 开始录音，开启一个新线程进行录音操作
    def start(self):
        self._running = True
        threading._start_new_thread(self.__record, ())
        threading._start_new_thread(self.__show, ())

    def showMicrophone(self):
        p = pyaudio.PyAudio()
        # 查找内录设备
        self.showInternalRecordingDevice(p)

    # 执行录音的线程函数
    def __record(self):
        self._running = True
        self._frames = []

        p = pyaudio.PyAudio()
        # 查找内录设备
        dev_idx = self.findInternalRecordingDevice(p)
        if dev_idx < 0:
            return
        # 在打开输入流时指定输入设备
        stream = p.open(
            input_device_index=dev_idx,
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK,
        )
        # 循环读取输入流
        while self._running:
            data = stream.read(self.CHUNK)
            if self._is_save:
                self._frames.append(data)
            wave_data = np.frombuffer(data, dtype=np.short)
            #2-N N维数组
            wave_data.shape = -1,2
            #将数组转置为 N-2 目标数组
            wave_data = wave_data.T
            if len(self._read_queue) >= self._read_queue_max_size:
                self._read_queue = self._read_queue[1:]
            self._read_queue.append(wave_data)
        # 停止读取输入流
        stream.stop_stream()
        # 关闭输入流
        stream.close()
        # 结束pyaudio
        p.terminate()
        return


    def __show(self):
        while self._running:
            if len(self._read_queue) == 0:
                continue
            wave_data = copy.copy(self._read_queue[0])
            for i, data in enumerate(self._read_queue):
                if i > 0:
                    wave_data = np.hstack((wave_data, data))
            wave_data = Denoise(wave_data, self.RATE, is_show=False)
            plt.pause(0.001)
        return


    # 停止录音
    def stop(self):
        self._running = False

    # 保存到文件
    def save(self, fileName):
        if self._is_save == False:
            print("ignore save audio")
            return
        p = pyaudio.PyAudio()
        wf = wave.open(fileName, "wb")
        
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        self._origin_data = b''.join(self._frames)
        wf.writeframes(self._origin_data)
        wf.close()

        wave_data = np.frombuffer(self._origin_data, dtype=np.short)
        print(wave_data.shape)
        #2-N N维数组
        wave_data.shape = -1,2
        #将数组转置为 N-2 目标数组
        wave_data = Denoise(wave_data, self.RATE)
        fileName = "filter_" + fileName
        wf = wave.open(fileName, "wb")
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(wave_data.tostring())
        print("filter_data len(%d)" % len(wave_data.tostring()))
        wf.close()

if __name__ == "__main__":

    if not os.path.exists("record"):
        os.makedirs("record")
    if not os.path.exists("filter_record"):
        os.makedirs("filter_record")

    print("Record Begin")
    rec = Recorder(1024, 2, 44100, False)
    begin_time = time.time()
    rec.start()
    range_time = 100
    begin_time = time.time()
    while 1:
        if time.time() - begin_time >= range_time:
            break
    rec.stop()
    audio_file_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_rate_" + str(rec.RATE) + ".wav"
    rec.save("record/" + audio_file_name)
    print('DBG: %s auido saved' % audio_file_name)
