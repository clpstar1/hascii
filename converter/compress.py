import numpy as np
import sys


def compress(np_arr_2D, compression_factor=4):
    np_arr_2D = reshape_into_chunk(np_arr_2D, tuple([compression_factor]*2))
    np_arr_2D = np_arr_2D.reshape(
        np_arr_2D.shape[0], np_arr_2D.shape[1], np_arr_2D.shape[2] * np_arr_2D.shape[3])
    np_arr_2D = np.average(np_arr_2D[0:][0:], axis=2)
    np_arr_2D = reshape_into_chunk(np_arr_2D, (4, 2))
    np_arr_2D = np_arr_2D.swapaxes(2, 3).reshape(
        np_arr_2D.shape[0], np_arr_2D.shape[1], np_arr_2D.shape[2] * np_arr_2D.shape[3])
    return np_arr_2D


def reshape_into_chunk(np_arr_2D, chunksize):
    arr_rowsz, arr_colsz = np_arr_2D.shape[0], np_arr_2D.shape[1]
    chunk_rowsz, chunk_colsz = chunksize

    lenr, lenc = int(
        np_arr_2D.shape[0]/chunk_rowsz), int(np_arr_2D.shape[1]/chunk_colsz)

    try:
        rs = np_arr_2D.reshape(lenr, chunk_rowsz, lenc, chunk_colsz)
        return rs.transpose(0, 2, 1, 3)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        print(
            f'probably caused by invalid chunskize: [ARR: {arr_rowsz}, {arr_colsz}] [CHUNK: {chunk_rowsz}, {chunk_colsz}], RETRYING:', file=sys.stderr)
    