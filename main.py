from PIL import Image
from more_itertools import take
from functools import reduce
from operator import lt, ge
from argparse import ArgumentParser
from split import splitH, splitV


def compress(array, blockdim, size): 
     
    x, y = blockdim 
    w, h = size 

    h_split = splitH(array, w * y)
    
    res = []
    for subl in h_split:

        v_split = splitV(subl, w, y)
        for subsubl in v_split:
            res.append(sum(subsubl) / len(subsubl))
    
    return res 

def print_lum(val, op, compare):
    if op(val, compare):
        print('.', end='')
    else:
        print('#', end='')

def print_ascii(luminance, invert, rowsz, compare = 128):
    i = 0
    for lum in luminance:
        i += 1
        if i % rowsz == 0:
            print('\n', end='')
        else: 
            if invert: 
                print_lum(lum, lt, compare)
            else: 
                print_lum(lum, ge, compare)

def get_divs(x_orig):
    x_orig

    divisors = []
    for rowsz in range(2, int(x_orig / 2)):
        if x_orig % rowsz == 0:
            divisors.append(rowsz)
    
    return divisors

def crop_even(img):
    x, y = img.size
    crop = False 
    if x % 2 != 0: x-=1; crop = True 
    if y % 2 != 0: y-=1; crop = True 

    if crop:
        img = img.crop((0, 0, x, y))
    return img 

if __name__ == '__main__':
    import sys

    parser = ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('-i', default=False, action='store_true')
    parser.add_argument('-c', default=128)

    args = parser.parse_args()

    # convert to black/white
    img = Image.open(args.filename).convert('LA')
    
    img = crop_even(img)

    x, y = img.size

    aspectRatio = x / y

    divs = get_divs(x)

    luminance = list(map(lambda data: data[0], img.getdata()))

    for div in divs:

        rows = int(x / div) 

        if rows > 40:
            cols = int(rows * (1/aspectRatio))
            
            xdim = int(x / rows)
            ydim = int(y / cols)

            res = compress(list(luminance), (xdim, ydim), (x, y))

            print_ascii(res, args.i, rows, int(args.c))