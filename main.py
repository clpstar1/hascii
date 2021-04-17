
from converter.reader_bmp import BMPWriter
from PIL import ImageFont

import sys
import subprocess as sp

if __name__ == '__main__':
    png = ''
    i = 0

    font = ImageFont.truetype(
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 8)

    cmd_out = ['ffmpeg',
               '-y',
               '-hide_banner',
               '-f', 'image2pipe',
               '-vcodec', 'bmp',
               '-i', '-',  # Indicated input comes from pipe
               '-vcodec', 'libx264',
               sys.argv[1]]

    subproc: sp.Popen = sp.Popen(
        cmd_out, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)

    bmp_writer = BMPWriter(1, subproc.stdin, font)

    while True:
        try:
            bmp_writer.read_bmp()
            i += 1
        except BrokenPipeError:
            out, err = subproc.communicate()
            print(out, err)
            exit(1)
