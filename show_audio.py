import wave
import pyaudio
import pylab
import numpy as np
import matplotlib.pyplot as plt

def get_framerate(wavefile):
    '''
        输入文件路径，获取帧率
    '''
    wf=wave.open(wavefile,"rb")#打开wav
    p = pyaudio.PyAudio()#创建PyAudio对象
    params = wf.getparams()#参数获取
    print(params)
    nchannels, sampwidth, framerate, nframes = params[:4]
    return framerate

def get_nframes(wavefile):
    '''
        输入文件路径，获取帧数
    '''
    wf=wave.open(wavefile,"rb")#打开wav
    p = pyaudio.PyAudio()#创建PyAudio对象
    params = wf.getparams()#参数获取
    nchannels, sampwidth, framerate, nframes = params[:4]
    return nframes
    
def get_wavedata(wavfile):
    '''
        输入文件路径，获取处理好的 N-2 左右声部数组
    '''
    #####1.读入wave文件
    wf=wave.open(wavfile,"rb")#打开wav
    p = pyaudio.PyAudio()#创建PyAudio对象
    params = wf.getparams()#参数获取
    nchannels, sampwidth, framerate, nframes = params[:4]
    stream = p.open(format=p.get_format_from_width(sampwidth),
                    channels=nchannels, 
                    rate=framerate,
                    output=True)#创建输出流
    #读取完整的帧数据到str_data中，这是一个string类型的数据
    str_data = wf.readframes(nframes)
    wf.close()#关闭wave

    #####2.将波形数据转换为数组
    # N-1 一维数组，右声道接着左声道
    wave_data = np.frombuffer(str_data, dtype=np.short)
    #2-N N维数组
    wave_data.shape = -1,2
    #将数组转置为 N-2 目标数组
    wave_data = wave_data.T
    return wave_data

def plot_timedomain(wave_data, framerate, nframes):
    '''
        画出时域图
    '''
    
    #####3.构建横坐标
    time = np.arange(0,nframes)*(1.0/framerate)

    #####4.画图
    pylab.figure("time_domain")
    pylab.subplot(211)
    pylab.plot(time, wave_data[0]) #第一幅图：左声道
    pylab.subplot(212)
    pylab.plot(time, wave_data[1], c="g") #第二幅图：右声道
    pylab.xlabel("time (seconds)")
    pylab.draw()
    pylab.pause(0.001)
    return None


def plot_freqdomain(start,fft_size,waveData, framerate):
    '''
        画出频域图
    '''
    
    #### 1.取出所需部分进行傅里叶变换，并得到幅值
    # rfft，对称保留一半，结果为 fft_size/2-1 维复数数组
    fft_y1 = np.fft.rfft(waveData[0][start:start+fft_size-1])/fft_size #左声部
    fft_y2 = np.fft.rfft(waveData[1][start:start+fft_size-1])/fft_size #右声部
   
    #### 2.计算频域图x值
    #最小值为0Hz，最大值一般设为采样频率的一半
    freqs = np.linspace(0, framerate//2, fft_size//2)

    #### 3.画图
    pylab.figure("frequence_domain")
    #plt.figure(figsize=(20,10))
    pylab.subplot(211)
    plt.plot(freqs, np.abs(fft_y1))
    pylab.xlabel("frequence(Hz)")
    pylab.subplot(212)
    plt.plot(freqs, np.abs(fft_y2),c='g')
    pylab.xlabel("frequence(Hz)")
    pylab.draw()
    pylab.show()

if __name__ == "__main__":
    wavfile = "record/2020-12-13_17-47-39_rate_44100.wav"
    waveData=get_wavedata(wavfile) #获取wave数据
    framerate=get_framerate(wavfile) #获取帧率数据
    nframes=get_nframes(wavfile) #获取帧数
    plot_timedomain(waveData, framerate, nframes)
    start_pos = 0
    plot_freqdomain(start_pos, len(waveData[0]) - start_pos, waveData, framerate)