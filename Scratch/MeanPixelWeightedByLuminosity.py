import numpy as np
import numpy.random as rnd
import time


def generate_mock_lightness_data(num_rows, num_cols):
    lightnesses = np.abs(rnd.randn(num_rows, num_cols))
    return lightnesses


def compute_weighted_centroid(lightnesses):
    num_rows, num_cols = lightnesses.shape
    x = np.arange(num_cols)
    y = np.arange(num_rows)

    centroid = [np.mean(lightnesses * x),
                np.mean(lightnesses * y[:, np.newaxis])]

    return centroid


# Script
lightnesses = generate_mock_lightness_data(1000, 1500)

start_time = time.time()

num_repeats = 10
for i in range(num_repeats):
    centroid = compute_weighted_centroid(lightnesses)

elapsed_time = time.time() - start_time
average_time = elapsed_time / num_repeats

print("Average time: %s seconds" % average_time)

## Output (when run on Jack's laptop) ##
#
#  Average time: 0.01668083667755127 seconds
#
