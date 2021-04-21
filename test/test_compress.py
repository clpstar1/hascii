from converter.compress import Compressor, reshape_into_chunk, get_padding
import unittest as ut
import numpy as np 


class TestCompress(ut.TestCase):

    def setUp(self) -> None:
        self.compressor = Compressor()

    def test_compress(self):
        arr = np.ones((16, 8))
        self.compressor.compress(arr, 1)

    def test_reshape(self):
        arr = np.ones((10, 11))
        reshape_into_chunk(arr, (4, 2))


    def test_get_padding(self):
        assert 0 == get_padding(8, 4)
        assert 3 == get_padding(5, 4)