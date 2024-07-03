import numpy as np
import matplotlib.pyplot as plt
import timeit
import random
import librosa
import panns_inference
import epanns_inference
from pathlib import Path
from epanns.models import Cnn14_pruned
import timeit

#'{}/panns_data/checkpoint_closeto_.44.pth'.format(str(Path.home()))

epanns_at = epanns_inference.AudioTagging(checkpoint_path="./epanns/checkpoint_closeto_.44.pt", 
                          model=Cnn14_pruned(sample_rate=48000, 
                                             window_size=1024,
                                             hop_size=320,
                                             mel_bins=64,
                                             fmin=50,
                                             fmax=14000,
                                             classes_num=527,
                                             p1=0,
                                             p2=0,
                                             p3=0,
                                             p4=0,
                                             p5=0,
                                             p6=0,
                                             p7=0.5,
                                             p8=0.5,
                                             p9=0.5,
                                             p10=0.5,
                                             p11=0.5,
                                             p12=0.5), 
                          device='cuda')

panns_at = panns_inference.AudioTagging(model=panns_inference.models.Cnn14(sample_rate=48000,window_size=1024, 
                hop_size=320, mel_bins=64, fmin=50, fmax=14000, classes_num=panns_inference.config.classes_num), device="cuda")

(audio, _) = librosa.core.load("./river_with_car_no_delay.wav", sr=48000, mono=True)

# Assuming 'audio' is already defined and is a 1-dimensional numpy array
audio_length = len(audio)

buffer_sizes = np.ndarray((100,), dtype=float)
panns_latency = np.ndarray((100,), dtype=float)
epanns_latency = np.ndarray((100,), dtype=float)

for i in range(32768, (32768 + (1024 * 100)), 1024):  # 307200
    if i > audio_length:
        break

    adj_index = int((i - 32768) / 1024)
    buffer_sizes[adj_index] = i
    print(i, adj_index)

    epanns_avg_samp = 0
    panns_avg_samp = 0

    for j in range(100):
        start_index = random.randint(0, audio_length - i)
        buffer_samples = audio[start_index:start_index + i]
        buffer_samples = buffer_samples[None, :]
        
        #print(f"analysing windown {start_index}:{start_index+i}")

        epanns_avg_samp = epanns_avg_samp + timeit.timeit("epanns_at.inference(buffer_samples)", globals=globals(), number=1)
        panns_avg_samp = panns_avg_samp + timeit.timeit("panns_at.inference(buffer_samples)\n\n", globals=globals(), number=1)

    print(f"epanns_avg_samp: {epanns_avg_samp}")
    epanns_latency[adj_index] = epanns_avg_samp / 100
    panns_latency[adj_index] = panns_avg_samp / 100


fig, ax = plt.subplots()
ax.plot(buffer_sizes, panns_latency, label='PANNS')
ax.plot(buffer_sizes, epanns_latency, label='E-PANNS')
ax.set(xlabel='Buffer Size', ylabel='Latency (ms)',
    title='Latency vs Buffer Size')
ax.grid(True)
ax.legend()
fig.savefig("panns.png")
buffer_samples.tofile("buffer_samples.csv", sep=",")
panns_latency.tofile("panns_latency.csv", sep=",")
epanns_latency.tofile("epanns_latency.csv", sep=",")
plt.show()