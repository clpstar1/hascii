import struct
import sys

import numpy as np
from PIL import Image

from converter.braille_mapper import Braille
from converter.compress import compress
from converter.numpy_util import numpy_avg_lum, numpy_map_2d
from converter.util import crop_even, draw_out_img, get_img_dims


def read_stdin(num_bytes):
    return sys.stdin.buffer.read(num_bytes)


class BMP:
    HEADER_BLK_SZ = 14
    INFO_BLK_SZ = 40

    HEADER_BLK_STRUCT = '<HIII'
    INFO_BLK_STRUCT = '<IiiHHIIiiII'

    def __init__(self):
        self.header_blk = None
        self.info_blk = None
        self.pixel_data = None
        self.bytes_read = 0

    def count(self, add_bytes):
        self.bytes_read += add_bytes

    def __read_header_blk(self):
        self.header_blk = BMPHeader(struct.unpack(
            BMP.HEADER_BLK_STRUCT, read_stdin(BMP.HEADER_BLK_SZ)))

        if self.header_blk.header != b'BM':
            raise ValueError(
                f'non bmp header received {self.header_blk.header}')

    def __read_info_blk(self):
        self.info_blk = BMPInfoBlock(struct.unpack(
            BMP.INFO_BLK_STRUCT, read_stdin(BMP.INFO_BLK_SZ)))

    def __read_pixels(self):
        offset = self.header_blk.offset
        # offset might be more than header + info
        if offset != BMP.HEADER_BLK_SZ + BMP.INFO_BLK_SZ:
            read_stdin(offset - (BMP.HEADER_BLK_SZ + BMP.INFO_BLK_SZ))
        self.pixel_data = read_stdin(self.info_blk.get_pixel_data_size())

    def get_size(self):
        if self.info_blk == None:
            raise TypeError('info_blk not initialized (use read() first)')
        return self.info_blk.get_size()

    def read(self):
        self.__read_header_blk()
        self.__read_info_blk()
        self.__read_pixels()

    def to_pil_greyscale_image(self):
        width, height = self.get_size()

        im = Image.frombytes('RGB', (width, height),
                             self.pixel_data).convert('L')
        return im


class BMPHeader:
    def __init__(self, header_block):
        self.header_block = header_block
        self.header = int.to_bytes(header_block[0], 2, 'little')
        self.offset = header_block[3]


class BMPInfoBlock:

    BI_RGB = 0

    def __init__(self, info_block):
        self.width = info_block[1]
        self.height = info_block[2]
        self.bitcount = info_block[4]
        self.compression = info_block[5]
        self.sizeimage = info_block[6]

    def is_bottom_up(self):
        return self.height >= 0

    def is_uncompressed(self):
        return self.compression == 0

    def get_pixel_data_size(self):
        if self.compression == BMPInfoBlock.BI_RGB:
            return self.sizeimage or self.width * abs(self.height) * 3
        raise ValueError('compressed bmp not implemented')

    def get_size(self):
        return self.width, self.height

    def __str__(self):
        return str(vars(self))


class BMPWriter:

    def __init__(self, compression_factor, dest, font):
        self.image_dims = None
        self.compression_factor = compression_factor
        self.dest = dest
        self.font = font
        self.braille = Braille()

    def read_bmp(self):

        # read bmp from stdin
        bmp: BMP = BMP()
        bmp.read()

        im = bmp.to_pil_greyscale_image()

        f, t, m = self.convert_from_bin(im, self.compression_factor)
        width, single_row_height = t

        img = Image.new('L', (width, single_row_height * len(m)), 'black')

        draw_out_img(m, img, f)

        if bmp.info_blk.is_bottom_up():
            img = img.transpose(Image.ROTATE_180)

        img.save(self.dest, 'BMP')

    def convert_from_bin(self, img_bytes, compression_factor):

        img = crop_even(img_bytes)

        width, _ = img.size

        lum = np.asarray(img)
        avg_lum = numpy_avg_lum(lum)

        lum2D = numpy_map_2d(lum, width)
        lum2D_compressed = compress(lum2D, compression_factor)

        if self.image_dims:
            out_image_dims = self.image_dims

        else:
            out_image_dims = get_img_dims(
                lum2D_compressed, self.font)
            self.image_dims = out_image_dims

        braille_mapped_image = self.braille.map_codes_to_symbols(
            lum2D_compressed, avg_lum, False)

        return (self.font, out_image_dims, braille_mapped_image)
