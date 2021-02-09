from PIL import Image
from more_itertools import take
from functools import reduce
from operator import lt, ge
from argparse import ArgumentParser


def splitH(array, rowsz): 
    res, tmp = ([], [])
    i = 0 
    for el in array: 
        i += 1 
        if i % rowsz == 0:
            tmp.append(el)
            res.append(tmp)
            tmp = []
        else:
            tmp.append(el)
    if len(tmp) > 0: res.append(tmp)
    
    return res


def splitV(array, rowsz, colsz):
    cols = int(rowsz / colsz) 
    res = []
    for i in range(0, cols):
        res.append([])
    colIndex = 0
    i = 0
    for el in array: 
        i += 1
        # switch col 
        if i % colsz == 0: 
            res[colIndex].append(el)
            colIndex = (colIndex + 1) % cols  
        else: 
            res[colIndex].append(el)

    return list(filter(lambda l : l != [], res))

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

def print_lum(val, op, compare = 128):
    if op(val, compare):
        print('.', end='')
    else:
        print('#', end='')

def print_ascii(luminance, invert, rowsz):
    i = 0
    for lum in luminance:
        i += 1
        if i % rowsz == 0:
            print('\n', end='')
        else: 
            if invert: 
                print_lum(lum, lt)
            else: 
                print_lum(lum, ge)

def print2D(array, rowsz):


if __name__ == '__main__':
    import sys

    parser = ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('-invert', default=False, action='store_true')

    args = parser.parse_args()

    # convert to black/white
    img = Image.open(args.filename).convert('LA')

    x, y = img.size 
    if x % 2 != 0: x -= 1
    if y % 2 != 0:  y -= 1

    img = img.crop((0, 0, 0 + x, 0 + y))

    aspectRatio = x / y

    luminance = list(map(lambda data: data[0], img.getdata()))


    xres = x / 2
    yres = int(xres * (1/aspectRatio))
    
    xdim = int(x / xres)
    ydim = int(y / yres)

    res = compress(list(luminance), (xdim, ydim), (x, y))

    print_ascii(res, args.invert, xres)