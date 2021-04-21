import struct
import subprocess as sp
import sys
from argparse import ArgumentParser

import numpy
import PIL as p
from PIL import ImageFont, ImageOps
from profilehooks import profile

from converter.bmp import BMPReader, BMPTransformer, BMPWriter
from converter.util import crop_even


def src_dst_from_args(args):
    if args.i:
            source = open(args.i, 'rb')
    else:
        source = sys.stdin.buffer

    if args.o:
        cmd_out = ['ffmpeg',
                '-loglevel', 'fatal',
                '-f', 'image2pipe',
                '-vcodec', 'bmp',
                '-i', '-',  # Indicated input comes from pipe 
                '-vcodec', 'libx264',
                args.o]

        ffmpeg_subprocess = sp.Popen(cmd_out, stdin=sp.PIPE)
        dest = ffmpeg_subprocess.stdin
    else:
        dest = sys.stdout.buffer
    
    return source, dest

@profile
def main():
    numpy.set_printoptions(threshold=sys.maxsize)
    ag = ArgumentParser()
    
    ag.add_argument('-i')
    ag.add_argument('-o')
    ag.add_argument('-c', nargs='+', type=int)
    ag.add_argument('-p', action='store_true')

    args = ag.parse_args()

    font = ImageFont.truetype('/usr/share/fonts/truetype/DejaVuSans.ttf', 8)

    source, dest = src_dst_from_args(args)
    comp = tuple(args.c) if args.c else (1,1)

    
    bmp_transformer = BMPTransformer(comp)
    bmp_writer = BMPWriter(dest, font, True, args.p)

    while True:
        bmp_reader = BMPReader(source)
        try: 
            bmp_reader.read()
            if args.p:
                print(str(bmp_reader))

            pil_greyscale_bmp = bmp_reader.to_pil_greyscale_image()

            pil_greyscale_bmp = crop_even(pil_greyscale_bmp)

            braille = bmp_transformer.map_to_braille_array(pil_greyscale_bmp)
            bmp_writer.write_braille_image(braille)

        except BrokenPipeError as e:
            print(e)
            source.close()
        except struct.error as e:
            print(e)
            source.close()
            sys.exit(0)



if __name__ == '__main__':

    main()
    

