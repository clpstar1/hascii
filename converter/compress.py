import sys

import numpy as np


class Compressor:

    BRAILLE_CHUNK_SIZE = (4,2)

    def __init__(self):
        self.padding = {}

    def map_to_braille_cells(self, np_array_2d):
        return self.compress(np_array_2d, Compressor.BRAILLE_CHUNK_SIZE)

    def compress_by_averages(self, np_array_2d, chunksize: tuple):
        # take averages across compression_factor x compression_factor cells
        if not is_divisible(np_array_2d, chunksize):
           np_array_2d = self._pad_array_2D(chunksize, np_array_2d)

        np_array_2d = reshape_into_chunk(np_array_2d, chunksize)
        np_array_2d = np_array_2d.reshape(np_array_2d.shape[0], np_array_2d.shape[1], -1)

        return np.average(np_array_2d, axis=2)
    
    def compress(self, np_array_2d, chunksize: tuple):
        #if not is_divisible(np_array_2d, chunksize):
        #    np_array_2d = self._pad_array_2D(chunksize, np_array_2d)

        # np_array_2d = np.pad(np_array_2d, [(0,0), (0,2)], constant_values=255)

        np_array_2d = reshape_into_chunk(np_array_2d, chunksize)
        
        tmp = np_array_2d.swapaxes(2,3).reshape(np_array_2d.shape[0], np_array_2d.shape[1], -1)

        return tmp

    def _pad_array_2D(self, chunksize:tuple, np_array_2d):
        arr_w, arr_h = np_array_2d.shape
        chk_w, chk_h = chunksize

        h_pad, w_pad = self._get_padding((arr_w, arr_h), (chk_w, chk_h))
        pad = np.pad(np_array_2d, [(h_pad, 0), (0, w_pad)], 'constant', constant_values=0)
        return pad

    def _get_padding(self, arr_dim, chunk_dim):
        try:
            return self.padding[arr_dim + chunk_dim]
        except KeyError:
            padding = (get_padding(arr_dim[0], chunk_dim[0]), get_padding(
                arr_dim[1], chunk_dim[1]))
            self.padding[arr_dim + chunk_dim] = padding
            return padding


def is_divisible(np_arr_2d, chunksize:tuple):
    arr_w, arr_h = np_arr_2d.shape
    chk_w, chk_h = chunksize

    if arr_w % chk_w != 0 or arr_h % chk_h != 0:
        return False
    return True


def reshape_into_chunk(np_arr_2D, chunksize:tuple):
    chunk_colsz, chunk_rowsz = chunksize
    lenc, lenr = int(np_arr_2D.shape[0]/chunk_colsz), int(np_arr_2D.shape[1]/chunk_rowsz)
    try:
        rs = np_arr_2D.reshape(lenc, chunk_colsz, lenr, chunk_rowsz)
        return rs.transpose(0, 2, 1, 3)

    except ValueError as e:
        print(str(e), file=sys.stderr)
        print(
            f'probably caused by invalid chunskize: [ARR: {np_arr_2D.shape}] [CHUNK: {chunk_rowsz}, {chunk_colsz}], RETRYING:', file=sys.stderr)

# a = 11
# b = 4


def get_padding(a, b):
    if b > a:
        raise ValueError

    if a == b:
        return 0


    diff = 0
    while a % b != 0:
        diff += 1
        a += 1

    return diff