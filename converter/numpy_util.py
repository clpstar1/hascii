import numpy as np

def numpy_map_2d(arr, rowsz):
    return np.reshape(arr, (-1, rowsz))


def numpy_LA_to_L(img):
    arr = np.array(img.getdata(), dtype=[('x', int), ('y', int)])
    return arr['x']


def numpy_avg_lum(lum):
    return np.average(lum)
