# coding in utf-8
# by rockycao
import math
import wave
import numpy as np
import pylab as pl
import volume as vp


def ZeroCR(waveData, frameSize, overLap):
    wlen = len(waveData)
    step = frameSize - overLap
    frameNum = math.ceil(wlen / step)
    zcr = np.zeros((frameNum, 1))
    for i in range(frameNum):
        curFrame = waveData[np.arange(i * step, min(i * step + frameSize, wlen))]
        # To avoid DC bias, usually we need to perform mean subtraction on each frame
        # ref: http://neural.cs.nthu.edu.tw/jang/books/audiosignalprocessing/basicFeatureZeroCrossingRate.asp
        curFrame = curFrame - np.mean(curFrame)  # zero-justified
        zcr[i] = sum(curFrame[0:-1] * curFrame[1::] <= 0)
    return zcr


# ============ test the algorithm =============
# read wave file and get parameters.
fw = wave.open('sample.wav', 'rb')
params = fw.getparams()
# print(params)
nchannels, sampwidth, framerate, nframes = params[:4]
str_data = fw.readframes(nframes)
wave_data = np.fromstring(str_data, dtype=np.short)
wave_data = wave_data[int(framerate * 60 * nchannels):framerate * 65 * nchannels]

wave_data.shape = -1, 1
fw.close()
frameSize = 256
overLap = 128

volume11 = vp.calVolume(wave_data, frameSize, overLap)
zcr = ZeroCR(wave_data, frameSize, overLap)
i = 0
voice = [0, 0]
flag_zcr = 0
flag_er = 0
split = []
zcr_mean = np.mean(zcr)
er_mean = np.mean(volume11)
time = np.arange(0, len(wave_data)) * (1.0 / framerate / nchannels)
time2 = np.arange(0, len(zcr)) * (len(wave_data) / len(zcr) / framerate / nchannels)
rate = 0.5
for i in range(len(zcr)):
    if zcr[i] >= zcr_mean and flag_er + flag_zcr == 0 and volume11[i] > rate * er_mean:
        flag_zcr = 1
        voice[0] = i
        print('zcr up')
    elif volume11[i] > rate * er_mean and flag_er + flag_zcr == 0:
        flag_er = 1
        voice[0] = i
        print('er up')
    elif flag_zcr == 1 and zcr[i] < rate * zcr_mean:
        flag_zcr = 0
        voice[1] = i
        if voice[1] - voice[0] > 10:
            split.append([voice[0], voice[1]])
        print('zcr down')
    elif flag_er == 1 and volume11[i] < rate * er_mean:
        flag_er = 0
        voice[1] = i
        if voice[1]-voice[0]>10:
            split.append([voice[0], voice[1]])
        print('er down')

f = open("span.txt", 'w')
num = 0
for span in split:
    num += 1
    f.write("{0}--{1}".format(span[0], span[1]))
    f.write('\n')
f.close()

for number in range(num):
    slice = wave.open(r"D:\github\audio\slice\%s.wav" % number, "wb")
    # 配置声道数、量化位数和取样频率
    slice.setnchannels(nchannels)
    slice.setsampwidth(sampwidth)
    slice.setframerate(framerate)
    # 将wav_data转换为二进制数据写入文件
    slice.writeframes(wave_data.tostring())
    slice.close()

pl.subplot(311)
pl.plot(time, wave_data)
pl.ylabel("wave")
pl.subplot(312)
pl.plot(time2, zcr)
pl.ylabel("ZCR")
pl.xlabel("time (seconds)")
pl.subplot(313)
pl.plot(time2, volume11)
pl.ylabel("volume")
pl.xlabel("time (seconds)")
sample = pl.gcf()
sample.savefig("sample")
pl.show()
