import struct
import sys

import numpy as np
from PIL import Image, ImageDraw

import converter.braille_mapper as bm
from converter.compress import Compressor
from converter.numpy_util import numpy_map_2d


class BMPReader:
    HEADER_BLK_SZ = 14
    INFO_BLK_SZ = 40

    HEADER_BLK_STRUCT = '<HIII'
    INFO_BLK_STRUCT = '<IiiHHIIiiII'

    def __init__(self, source):
        self.source = source
        self.header_blk: BMPHeader = None
        self.info_blk: BMPInfoBlock = None
        self.pixel_data = []

    def read_n_bytes(self, num_bytes):
        return self.source.read(num_bytes)

    def __read_header_blk(self):
        self.header_blk = BMPHeader(struct.unpack(
            BMPReader.HEADER_BLK_STRUCT, self.read_n_bytes(BMPReader.HEADER_BLK_SZ)))

        if self.header_blk.header != b'BM':
            raise ValueError(
                f'non bmp header received {self.header_blk.header}')

    def __read_info_blk(self):
        self.info_blk = BMPInfoBlock(struct.unpack(
            BMPReader.INFO_BLK_STRUCT, self.read_n_bytes(BMPReader.INFO_BLK_SZ)))

    def __read_pixels(self):
        offset = self.header_blk.offset
        # offset might be more than header + info
        if offset != BMPReader.HEADER_BLK_SZ + BMPReader.INFO_BLK_SZ:
            self.read_n_bytes(
                offset - (BMPReader.HEADER_BLK_SZ + BMPReader.INFO_BLK_SZ))

        width, height = self.get_size()

        pixels = self.read_n_bytes(
            self.info_blk.get_pixel_data_size())

        self.pixel_data = bytearray()
        # bmp files are padded so that every new row starts at % 4 == 0
        if width % 4 != 0: 
            padding = 0
            while (width+padding) % 4 != 0:
                padding += 1 
        
            bytes_per_pixel = self.info_blk.bitcount // 8 
            bytes_per_row = width * bytes_per_pixel + padding

            prev_width = 0
            width = bytes_per_row
            # cut off padding after each row.
            for _ in range(0, height):
                self.pixel_data += pixels[prev_width: width - padding]
                prev_width += bytes_per_row 
                width += bytes_per_row
        else:
            self.pixel_data = pixels


    def get_size(self):
        if self.info_blk == None:
            raise TypeError('info_blk not initialized (use read() first)')
        return self.info_blk.get_size()

    def is_bottom_Up(self):
        return self.info_blk.is_bottom_up()

    def read(self):
        """read bmp data from given stream and return the raw pixel data

        Returns:
            [type]: [description]
        """
        self.__read_header_blk()
        self.__read_info_blk()
        self.__read_pixels()

    # ! TODO IF 32 BIT THIS NEEDS TO BE RGBA ! ! ! 
    def to_pil_greyscale_image(self):
        width, height = self.get_size()
        if self.info_blk.bitcount == 32:
            rgb = Image.frombytes('RGBA', (width, height),self.pixel_data)
        elif self.info_blk.bitcount == 24:
            rgb = Image.frombytes('RGB', (width, height), bytes(self.pixel_data))
        else:
            raise ValueError(f'not implemented {self.info_blk.bitcount} bitcount')
        gs = rgb.convert('L')
        return gs

    def to_pil_image(self):
        width, height = self.get_size()

        im = Image.frombytes('RGB', (width, height),
                             self.pixel_data)
        return im

    def __str__(self):
        return self.header_blk.__str__() + '\n' + self.info_blk.__str__()


class BMPHeader:
    def __init__(self, header_block):
        self.header_block = header_block
        self.header = int.to_bytes(header_block[0], 2, 'little')
        self.offset = header_block[3]

    def __str__(self):
        return str(vars(self))


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
    def __init__(self, dest, font, bottom_up, print_rows=False):
        self.dest = dest
        self.font = font
        self.bottom_up = bottom_up
        self.print_rows = print_rows

        self.image_dims = None

    def write_braille_image(self, braille_array):
        """
        writes the braille mapped image to self.dest
        """

        width, single_row_height = self._get_image_dims(braille_array)
        height = single_row_height * (len(braille_array))
        print(width, height)

        out_image = Image.new('L', (width, height), 'black')

        # draws the braille strings onto a pil image (takes long)
        draw_out_img(braille_array, out_image, self.font, self.print_rows), 

        # flip image vertically since BMP starts from bottom right corner
        if self.bottom_up:
            out_image = out_image.transpose(Image.ROTATE_180)

        if not self.print_rows:
            out_image.save(self.dest, 'BMP')

    def _get_image_dims(self, braille_image):
        if self.image_dims:
            return self.image_dims
        else:
            out_image_dims = get_img_dims(len(braille_image[0]), self.font)
            self.image_dims = out_image_dims
            return self.image_dims


class BMPTransformer:
    """
    reads bmp images from stdin and transforms them to braille strings   
    """

    def __init__(self, compression_chunksize, invert=False):

        self.compression_chunk_size = compression_chunksize
        self.invert = invert

    def map_to_braille_array(self, pil_greyscale_img):
        compressor = Compressor()
        braille_mapper = bm.BrailleMapper()

        luminance_2d = np.asarray(pil_greyscale_img)
        average_luminance = np.average(luminance_2d)

        # take AxB Chunks and average them to a single value.
        luminance_2d = compressor.compress_by_averages(
           luminance_2d, self.compression_chunk_size)
        # map to 2x4 Cells
        luminance_2d = compressor.map_to_braille_cells(luminance_2d)

        return braille_mapper.map_codes_to_symbols(luminance_2d, average_luminance, self.invert)


def draw_out_img(charmap2D, out_image, font, print_rows=False):
    draw = ImageDraw.Draw(out_image)
    image_str = ''

    for row in charmap2D:
        if print_rows:
            print(row)
        image_str += row + '\n'

    draw.multiline_text((0, 0), image_str, font=font, fill='white')


def get_img_dims(rowsz, font):
    width, single_row_height = font.getsize('⣿' * rowsz)
    return (width, single_row_height)


