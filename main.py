import math
import wave
import numpy as np
import pylab as pl
import volume as vp

def ZeroCR(waveData,frameSize,overLap):
    wlen = len(waveData)
    step = frameSize - overLap
    frameNum = math.ceil(wlen/step)
    zcr = np.zeros((frameNum,1))
    for i in range(frameNum):
        curFrame = waveData[np.arange(i*step,min(i*step+frameSize,wlen))]
        #To avoid DC bias, usually we need to perform mean subtraction on each frame
        #ref: http://neural.cs.nthu.edu.tw/jang/books/audiosignalprocessing/basicFeatureZeroCrossingRate.asp
        curFrame = curFrame - np.mean(curFrame) # zero-justified
        zcr[i] = sum(curFrame[0:-1]*curFrame[1::]<=0)
    return zcr

def get_energy(waveData,frameSize,overLap):
    wlen = len(waveData)
    step = frameSize - overLap
    frameNum = math.ceil(wlen / step)

# ============ test the algorithm =============
# read wave file and get parameters.
fw = wave.open('sample.wav','rb')
params = fw.getparams()
#print(params)
nchannels, sampwidth, framerate, nframes = params[:4]
str_data = fw.readframes(nframes)
wave_data = np.fromstring(str_data, dtype=np.short)
wave_data = wave_data[int(framerate*60*nchannels):framerate*61*nchannels]
f = wave.open(r"D:\github\audio\small.wav", "wb")

# 配置声道数、量化位数和取样频率
f.setnchannels(nchannels)
f.setsampwidth(sampwidth)
f.setframerate(framerate)
# 将wav_data转换为二进制数据写入文件
f.writeframes(wave_data.tostring())
f.close()
wave_data.shape = -1, 1
#wave_data = wave_data.T
fw.close()

# calculate Zero Cross Rate
frameSize = 256
overLap = 128
volume11 = vp.calVolume(wave_data,frameSize,overLap)
# volume12 = vp.calVolumeDB(wave_data,frameSize,overLap)
zcr = ZeroCR(wave_data,frameSize,overLap)
i = 0
voice = [0,0]
flag = 0
flag_zcr = 0
flag_er = 0
split = []
zcr_mean = np.mean(zcr)
er_mean = np.mean(volume11)
time = np.arange(0, len(wave_data)) * (1.0 / framerate/nchannels)
time2 = np.arange(0, len(zcr)) * (len(wave_data)/len(zcr) / framerate/nchannels)
for i in range(len(zcr)):
    if flag == 0 and abs(frame) >= 500:
        if wave_data[i+5] >= 500:
            if zcr[i]> zcr_mean:
                flag_zcr = 1
                print("zcr_up")
            elif volume11[i] > er_mean:
                flag_er = 1
                print("er_up")
            else:
                break
            flag = 1
            voice[0] = i
            print(i)
    elif flag == 1:
        if flag_zcr == 1:
            if zcr[i] < zcr_mean:
                flag_zcr = 0
                flag = 0
                voice[1] = i
                print("zcr_down")
            else:
                continue
        elif flag_er == 1:
            if volume11[i]<er_mean:
                flag_er = 0
                flag = 0
                voice[1] = i
                print("er_down")
            else:
                continue
        if flag == 0:
            split.append([voice[0],voice[1]])

f = open("span.txt",'w')
for span in split:
    f.write("{0}--{1}".format(span[0],span[1]))
    f.write('\n')
f.close()

# plot the wave

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
#pl.subplot(314)
#pl.plot(time2, volume12, c="g")
#pl.ylabel("Decibel(dB)")
pl.xlabel("time (seconds)")
sample = pl.gcf()
sample.savefig("sample")
pl.show()


