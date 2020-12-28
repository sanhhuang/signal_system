# _*_ coding: utf-8 _*_

import os
import pyaudio
import threading
import wave
import time
from datetime import datetime

class Recorder:
    def __init__(self, chunk=1024, channels=2, rate=44100):
        self.CHUNK = chunk
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = channels
        self.RATE = rate
        self._running = True
        self._frames = []

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
        threading._start_new_thread(self.__record, ())

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
            self._frames.append(data)

        # 停止读取输入流
        stream.stop_stream()
        # 关闭输入流
        stream.close()
        # 结束pyaudio
        p.terminate()
        return

    # 停止录音
    def stop(self):
        self._running = False

    # 保存到文件
    def save(self, fileName):
        p = pyaudio.PyAudio()
        wf = wave.open(fileName, "wb")
        
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)

        wf.writeframes(b"".join(self._frames))
        wf.close()


if __name__ == "__main__":

    if not os.path.exists("record"):
        os.makedirs("record")

    print("Record Begin")
    rec = Recorder(1024, 2, 44100)
    begin_time = time.time()
    rec.start()
    range_time = 10.5
    begin_time = time.time()
    while 1:
        if time.time() - begin_time >= range_time:
            break
    rec.stop()

    audio_file_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_rate_" + str(rec.RATE) + ".wav"
    print('DBG: %s auido saved' % audio_file_name)
    rec.save("record/" + audio_file_name)
