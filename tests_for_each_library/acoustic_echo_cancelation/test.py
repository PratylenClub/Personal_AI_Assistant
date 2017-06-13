import numpy as np
import matplotlib.pyplot as plt
import adaptfilt as adf

# Get u(n) - this is available on github or pypi in the examples folder
u = np.load('speech.npy')
print u
# Generate received signal d(n) using randomly chosen coefficients
coeffs = np.concatenate(([0.8], np.zeros(8), [-0.7], np.zeros(9),
                         [0.5], np.zeros(11), [-0.3], np.zeros(3),
                         [0.1], np.zeros(20), [-0.05]))

d = np.convolve(u, coeffs)

# Add background noise
v = np.random.randn(len(d)) * np.sqrt(5000)
d += v

# Apply adaptive filter
M = 100  # Number of filter taps in adaptive filter
step = 0.1  # Step size
y, e, w = adf.nlms(u, d, M, step, returnCoeffs=True)
help(adf.nlms)
# Calculate mean square weight error
mswe = adf.mswe(w, coeffs)

# Plot speech signals
plt.figure()
plt.title("Speech signals")
plt.plot(u, label="Emily's speech signal, u(n)")
plt.plot(d, label="Speech signal from John, d(n)")
plt.plot(y, label="Speech signal filtered, w(n)")
plt.grid()
plt.legend()
plt.xlabel('Samples')

# Plot error signal - note how the measurement noise affects the error
plt.figure()
plt.title('Error signal e(n)')
plt.plot(e)
plt.grid()
plt.xlabel('Samples')

# Plot mean squared weight error - note that the measurement noise causes the
# error the increase at some points when Emily isn't speaking
plt.figure()
plt.title('Mean squared weight error')
plt.plot(mswe)
plt.grid()
plt.xlabel('Samples')

# Plot final coefficients versus real coefficients
plt.figure()
plt.title('Real coefficients vs. estimated coefficients')
plt.plot(w[-1], 'g', label='Estimated coefficients')
plt.plot(coeffs, 'b--', label='Real coefficients')
plt.grid()
plt.legend()
plt.xlabel('Samples')

plt.show()