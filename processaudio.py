# _*_ coding: utf-8 _*_

import os
import pyaudio
import threading
import wave
import time
import matplotlib.pyplot as plt
import numpy as np
import copy
from scipy import signal
from datetime import datetime


def FilterSingleAudio(single_wave_data, rate, filter_freq):
    b, a = signal.butter(8, (filter_freq * 2)/rate,
                         'highpass')  # 配置滤波器 8 表示滤波器的阶数
    return signal.filtfilt(b, a, single_wave_data).astype('int16')  # data为要过滤的信号

def FilterAudio(wave_data, rate, filter_freq):
    if len(wave_data.shape) == 2:
        for i in range(wave_data):
            wave_data[i] = FilterSingleAudio(wave_data[i], rate, filter_freq)
    else:
        wave_data = FilterSingleAudio(wave_data, rate, filter_freq)
    
    return wave_data