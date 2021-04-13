import numpy as np 
from profilehooks import profile

def compress(lum, compression_factor=4):
        lum = reshape_into_chunk(lum, tuple([compression_factor]*2))
        lum = lum.reshape(lum.shape[0], lum.shape[1], lum.shape[2] * lum.shape[3])
        lum = np.average(lum[0:][0:], axis=2)
        lum = reshape_into_chunk(lum, (4, 2))
        lum = lum.swapaxes(2,3).reshape(lum.shape[0], lum.shape[1], lum.shape[2] * lum.shape[3])
        return lum

def reshape_into_chunk(lum, chunksize):
    a = lum
    rowsize, colsize = chunksize
    lenr, lenc = int(a.shape[0]/rowsize), int(a.shape[1]/colsize)

    rs = a.reshape(lenr, rowsize, lenc, colsize)
    t = rs.transpose(0, 2, 1, 3)

    return t 