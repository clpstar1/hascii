import struct
import sys

import numpy as np
from PIL import Image

import converter.braille_mapper as braille_mapper
from converter.compress import Compressor
from converter.util import crop_even, draw_out_img, get_img_dims
from converter.numpy_util import numpy_map_2d

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
        """read bmp data from stdin and return the raw pixel data

        Returns:
            [type]: [description]
        """        
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



class BMPTransformer:
    """
    reads bmp images from stdin and transforms them to braille strings   
    """
    def __init__(self, compression_factor, dest, font):
        
        self.compression_factor = compression_factor
        self.dest = dest
        self.font = font

        self.braille = braille_mapper.Braille()
        self.image_dims = None
        self.luminance_data = []
        self.average_luminance = 0

    def write_braille_image(self):
        """reads bmp data from stdin and writes to self.dest
        """        
        # read bmp from stdin
        bmp: BMP = BMP()
        bmp.read()
        # map to greyscale
        greyscale_img = bmp.to_pil_greyscale_image()
        # crop to even dimensions
        greyscale_img = crop_even(greyscale_img)
        # create array of braille strings
        braille_image = self.map_to_braille_image(greyscale_img, self.compression_factor)

        width, single_row_height = self._get_image_dims()
        height = single_row_height * len(braille_image[0])

        out_image = Image.new('L', (width, height), 'black')
        
        # draws the braille strings onto a pil image (takes long)
        draw_out_img(braille_image, out_image, self.font)

        # flip image vertically since BMP starts from bottom right corner
        if bmp.info_blk.is_bottom_up():
            out_image = out_image.transpose(Image.ROTATE_180)

        out_image.save(self.dest, 'BMP')

    def map_to_braille_image(self, pil_greyscale_img, compression_factor):
        
        width, _ = pil_greyscale_img.size
        self.luminance_data = np.asarray(pil_greyscale_img)
        self.average_luminance = np.average(self.luminance_data)
        # map to 2d
        
        luminance_2d = numpy_map_2d(self.luminance_data, width)
        
        compressor = Compressor()
        # take AxB Chunks and average them to a single value.
        self.luminance_data = compressor.compress_by_averages(luminance_2d, (compression_factor, compression_factor))

        # map to 2x4 Cells 
        self.luminance_data = compressor.map_to_braille_cells(self.luminance_data)

        return self.braille.map_codes_to_symbols(self.luminance_data, self.average_luminance, False)

        
    def _get_image_dims(self):
        if self.image_dims:
            return self.image_dims
        else:
            out_image_dims = get_img_dims(len(self.luminance_data[0]), self.font)
            self.image_dims = out_image_dims
            return self.image_dims


    