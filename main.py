# coding in utf-8
# by rockycao

import wave

import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans

times = 11
num = 10
# todo:use librosa
fw = wave.open('1_2.wav', 'rb')
params = fw.getparams()
nchannels, sampwidth, framerate, nframes = params[:4]
str_data = fw.readframes(nframes)
fw.close()
wave_data = np.fromstring(str_data, dtype=np.short)
wave_data.shape = -1, 1
wave_data = wave_data.T
time = np.arange(0, nframes) * (1.0 / framerate / nchannels)
end_time = time[-1]
norm_time = time * framerate * times  # k-means时正则化
wave = np.dstack((wave_data, norm_time)).reshape(-1, 2)
wave = np.array(wave)

'''wave_split = []
for frame in wave:
    if frame[0] > 0.1 * framerate:
        wave_split.append(frame)
wave_split = np.array(wave_split)
'''
y_pred = KMeans(n_clusters=10).fit_predict(wave)
time = np.delete(wave, 0, axis=1)
time = time / framerate / times
plt.scatter(wave[:, 1], wave[:, 0] / framerate / times, c=y_pred)
plt.savefig("sample")
plt.show()

time_string = np.dstack((time, y_pred.reshape(-1, 1))).reshape(-1, 2)
a = np.full((num, 1), end_time)
b = np.zeros((num, 1))
a = np.dstack((a, b)).reshape(-1, 2)

for i in time_string:
    num = int(i[1])
    t = i[0]
    if t < a[num][0]:
        a[num][0] = t
    elif t > a[num][1]:
        a[num][1] = t
a = a[a[:, 0].argsort()]
f = open("span.txt", 'w')
for i in a:
    f.write("{}--{}\n".format(i[0], i[1]))
f.close()
