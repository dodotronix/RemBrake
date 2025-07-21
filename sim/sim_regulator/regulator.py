import numpy as np
import matplotlib.pyplot as plt

# system constants
fs_update = 1e-3
fs_measure = 1e-2
servo_speed = 0.16 # s/60deg
servo_v = 60/servo_speed
servo_step = servo_v*fs_update
samples = int(fs_measure//fs_update)

a = 5e-2
angle = np.linspace(0, 120, 660)
print(angle)
current = -(a*(angle - 30))**-2

# PID REGULATOR
# consts
N = 150
p = 100
d = 0
i = 0

# the measurement is negative
# BMS chip to measure the current
regulate_to = -0.5

# variables
pid_angle = np.zeros(N)
measured_current = np.zeros(N)
actual = np.zeros(N)
error = np.zeros(N-1)

# init values
pid_angle[0] = 100
z = -(a*(pid_angle[0] - 30))**-2

measured_current[0] = z
prev = z

for n in range(1, N):
    pass

#    error[n-1] = regulate_to - z
#    delta = p*error[n-1]
#    pid_angle[n] = pid_angle[n-1] + delta
#
#    # limit the angle
#    # TODO the limits are incorrectly set or used
#    pid_angle[n] = np.clip(pid_angle[n], 30.1, 120)
#
#    # electric current measurement
#    z = -(a*(pid_angle[n] - 30))**-2
#    measured_current[n] = z

fig, axs = plt.subplots(nrows=3, ncols=1, figsize=(8, 10))
axs[0].set_title("Electric current servo profile")
axs[0].plot(angle, current, label="profile")
axs[0].set_xlabel("Angle [deg]")
axs[0].set_ylabel("Current [A]")
axs[0].legend(fontsize=16)
axs[0].grid(True)

axs[2].set_title("Open loop control")
axs[2].plot(actual, "-o", label="angle")
axs[2].set_xlabel("time [s]")
axs[2].set_ylabel("Angle [deg]")
axs[2].legend(fontsize=16)
axs[2].grid(True)

# axs[1].set_title("PID regulator angle control")
# axs[1].plot(pid_angle, "-o", label="angle")
# axs[1].set_xlabel("Steps [-]")
# axs[1].set_ylabel("Angle [deg]")
# axs[1].legend(fontsize=16)
# axs[1].grid(True)
#
# axs[2].set_title("PID input current measurements")
# axs[2].plot(error, "-o", label="error")
# axs[2].plot(measured_current, "-o", label="current")
# axs[2].set_xlabel("Steps [-]")
# axs[2].set_ylabel("Current [A]")
# axs[2].legend(fontsize=16)
# axs[2].grid(True)

plt.tight_layout(h_pad=1, w_pad=1)
plt.show()