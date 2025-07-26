#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt

data = np.loadtxt("data.csv", delimiter=',', skiprows=1)
angle = data[:, 0]

plt.figure(0)
plt.plot(angle, data[:, 1], label='chip')
plt.plot(angle, data[:, 2], label='lab')
plt.legend(fontsize=16)
plt.grid(True)

plt.show()
