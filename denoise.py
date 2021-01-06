import numpy as np
import numpy.fft as nf
import matplotlib.pyplot as plt
import scipy.io.wavfile as sw

def Denoise(sigs, sample_rate, is_plt=True, is_show=True):
    if sigs.shape[1] == 2:
        filter_sigs_1 = SingleDenoise(sigs[:, 0], sample_rate, is_plt, is_show)
        # filter_sigs_2 = SingleDenoise(sigs[:, 1], sample_rate, is_plt=False, is_show=False)
        return np.c_[filter_sigs_1, filter_sigs_1]
    else:
        filter_sigs_1 = SingleDenoise(sigs[0], sample_rate, is_plt, is_show)
        # filter_sigs_2 = SingleDenoise(sigs[1], sample_rate, is_plt=False, is_show=False)
        return np.c_[filter_sigs_1, filter_sigs_1].T

def SingleDenoise(sigs, sample_rate, is_plt=True, is_show=True):

    times = np.arange(sigs.size) / sample_rate
    # fft变换
    freqs = nf.fftfreq(sigs.size, times[1] - times[0])
    comp_arr = nf.fft(sigs)
    pows = np.abs(comp_arr)
    # 在频谱中去除噪声
    condition = ((np.abs(freqs) > 50) & (np.abs(freqs) < 4000))
    comp_arr = np.where(condition, comp_arr, 0)
    filter_pows = np.abs(comp_arr)
    # 逆向傅里叶变换
    filter_sigs = nf.ifft(comp_arr).real
    if is_plt == False:
        return (filter_sigs).astype(np.int16)

    # 绘图
    plt.figure('Filter', facecolor='lightgray')
    plt.clf()

    ax = plt.subplot(221)
    plt.plot(times, sigs, color='dodgerblue')
    ax.set_title('Origin Time Domain', fontsize=12)
    ax.set_ylabel('Origin Signal', fontsize=12)
    plt.grid(linestyle=':')
    plt.tight_layout()


    ax = plt.subplot(222)
    plt.semilogy(freqs[freqs > 0], pows[freqs > 0], color='orangered')
    ax.set_title('Origin Frequency Domain', fontsize=12)
    ax.set_ylabel('Origin Pow', fontsize=14)
    plt.grid(linestyle=':')
    plt.tight_layout()
    
    ax = plt.subplot(224)
    plt.semilogy(freqs[freqs > 0], filter_pows[freqs > 0], color='orangered')
    ax.set_ylabel('Filter Pow', fontsize=14)
    plt.grid(linestyle=':')
    ax.set_title('Filter Frequency Domain', fontsize=12)
    plt.tight_layout()

    ax = plt.subplot(223)
    plt.plot(times, filter_sigs, color='dodgerblue')
    ax.set_ylabel('Filter Signal', fontsize=12)
    plt.grid(linestyle=':')
    ax.set_title('Filter Time Domain', fontsize=12)
    # plt.legend()
    plt.tight_layout()
    if is_show:
        plt.show()
    else:
        plt.draw()
    
    return (filter_sigs).astype(np.int16)

if __name__ == "__main__":
    sample_rate, sigs = sw.read('./record/2021-01-06_20-39-27_rate_44100.wav')
    sigs = Denoise(sigs, sample_rate)
    sw.write('./filter_record/filter.wav', sample_rate, sigs)