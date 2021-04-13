from PIL import Image, ImageFont
from util import crop_even, draw_out_img, get_img_dims
from numpy_utils import numpy_avg_lum, numpy_map_2d
from braille import map_codes_to_symbols
import numpy as np
from compress import compress
import sys
import struct
import subprocess as sp
from profilehooks import profile


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
        self.header_blk = BMPHeader(struct.unpack(BMP.HEADER_BLK_STRUCT, read_stdin(BMP.HEADER_BLK_SZ)))

        if self.header_blk.header != b'BM':
            raise ValueError(f'non bmp header received {self.header_blk.header}')
    
    def __read_info_blk(self):
        self.info_blk = BMPInfoBlock(struct.unpack(BMP.INFO_BLK_STRUCT, read_stdin(BMP.INFO_BLK_SZ)))
    
    def __read_pixels(self):
        offset = self.header_blk.offset
        # offset might be more than header + info 
        if offset != BMP.HEADER_BLK_SZ + BMP.INFO_BLK_SZ:
            read_stdin(offset - (BMP.HEADER_BLK_SZ + BMP.INFO_BLK_SZ))
        self.pixel_data = read_stdin(self.info_blk.get_pixel_data_size())
        # reverse the list for further processing
        # if self.info_blk.is_bottom_up():
        #     self.pixel_data = self.pixel_data[::-1]

    def get_size(self):
        if self.info_blk == None:
            raise TypeError('info_blk not initialized (use read() first)')
        return self.info_blk.get_size()

    def read(self):
        self.__read_header_blk()
        self.__read_info_blk()
        self.__read_pixels()

class BMPHeader:
    def __init__(self, header_block):
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
            return self.width * abs(self.height) * 3
        raise ValueError('compressed bmp not implemented')
    
    def get_size(self):
        return self.width, self.height

class BMPReader:

    def __init__(self):
        self.image_dims = None

    @profile
    def read_bmp(self, pipe, compression_factor):

        # read bmp from stdin
        bmp: BMP = BMP()
        bmp.read()

        width, height = bmp.get_size()

        im = Image.frombytes('RGB', bmp.get_size(), bmp.pixel_data).convert('L')

        f, t, m = self.convert_from_bin(im, compression_factor)

        img = Image.new('L', (t[0], t[1]*len(m)), 'black')
        draw_out_img(m, img, t[1], f)
        img = img.transpose(Image.ROTATE_180)

        img.save(pipe.stdin, 'BMP')
    
    
    def convert_from_bin(self, img_bytes, compression_factor):

        img = crop_even(img_bytes)

        width, height = img.size

        lum = np.asarray(img)
        avg_lum = numpy_avg_lum(lum)

        lum2D = numpy_map_2d(lum, width)
        lum2D_compressed = compress(lum2D, compression_factor)
        
        if self.image_dims:
            out_image_dims = self.image_dims
        else:
            out_image_dims = get_img_dims(lum2D_compressed, font, avg_lum, False)
            self.image_dims = out_image_dims
      

        braille_mapped_image = map_codes_to_symbols(lum2D_compressed, font, avg_lum, False)

        return (font, out_image_dims, braille_mapped_image)
                

if __name__ == '__main__':
    png = ''
    i = 0

    font = ImageFont.truetype('/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf', 12)

    cmd_out = ['ffmpeg',
            '-loglevel', 'fatal',
            '-f', 'image2pipe',
            '-vcodec', 'bmp',
            '-i', '-',  # Indicated input comes from pipe 
            '-vcodec', 'libx264',
            'video.mp4']

    pipe = sp.Popen(cmd_out, stdin=sp.PIPE)

    bmp_reader = BMPReader()

    while True:
        try: 
            bmp_reader.read_bmp(pipe, 4)
            i+=1
        except struct.error:
            
            exit(0)