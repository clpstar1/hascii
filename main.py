# -*- coding: utf-8 -*-

from PIL import Image
from more_itertools import take
from functools import reduce
from operator import lt, ge
from argparse import ArgumentParser
from split import splitH, splitV


def crop_even(img):
    """shaves of pixels to make img even in dimension
    e.g 1024x1025 -> 1024x1024 

    Args:
        img ([type]): pointer to opened PIL Image

    Returns:
        [type]: the new image
    """    
    x, y = img.size
    crop = False 
    if x % 2 != 0: x-=1; crop = True 
    if y % 2 != 0: y-=1; crop = True 

    if crop:
        img = img.crop((0, 0, x, y))
    return img 

def bin_to_arr(num, bits = 8):
    """ converts a binary number to an array of ints 

    Args:
        num ([type]): the binary number to be converted
        bits (int, optional): the width of the number. Defaults to 8.

    Returns:
        [type]: array that contains every pixel from the original number
        beginning with the highest bit 
    """    
    res = []
    for i in range(0, bits):
        res.append(1 if num & 1 << i > 0 else 0)
    res = list(reversed(res))
    return res 

def arr_to_bin(arr):
    """ converts an array of integers to a binary number, starting from the highest bit
        e.g arr_to_bin([1,0,1,0], 4) => 0b1010
    Args:
        arr ([type]): array containing the individual bits

    Returns:
        [type]: a binary representation of the array
    """    
    res = 0
    for i in range(len(arr)-1, -1, -1):
        res += arr[i] * (2 ** i)
    return res

def get_braille_char(arr):
    """ takes an array of bits and returns the braille representation of that array.
    the highest bit represents the upper left dot. breaks into a new column after
    the 4th bit. array MUST be 8 bits long
    e.g 
    [0,0,0,1,1,1,1,1,1] => ⣰

    Args:
        arr ([type]): array representing the braille

    Returns:
        [type]: the unicode braille char 
    """     
    def swap(x, y):
        tmp = arr[x]
        arr[x] = arr[y]
        arr[y] = tmp 

    swap(3,4)
    swap(4,5)
    swap(5,6)
    # 10240 is the base of the braille unicode block
    return chr(arr_to_bin(arr) + 10240)

def get_chunk(offset, chunksize, arr):
    """slices a chunk out of a 2d array 

    Args:
        offset ([type]): tuple containing x and y offset
        chunksize ([type]): tuple containing the dimension of the chunk
        lums ([type]): the 2d array (in this usecase the greyscale image values)

    Returns:
        a sliced chunk of the original array 
    """    
    res = []
    xsize, ysize = chunksize
    xoff, yoff = offset
    for i in range(0, xsize):
        for j in range(0, ysize):
            res.append(arr[j+yoff][i+xoff])
    return res 

def map2D(arr, rowsz):
    """maps a 1d array of into a 2d array wrappin on rowsz 

    Args:
        arr ([type]): the original array
        rowsz ([type]): the number of columns after which the array should start a new row 

    Returns:
        [type]: 2d representation of the original array
    """
    res = []
    y = -1
    for el, idx in zip(arr, range(0, len(arr))): 
        if idx % rowsz == 0:
            res.append([])
            y += 1 
        res[y].append(el)
    return res 
    

def compress2D(lums, chunksize, average=True): 
    """ compresses a 2d array given dimensions of chunksize
    if average is false, just groups per chunk in x and y direction

    e.g
    avg = false, chunksize = 2, 4
    [
        [1,2,3,4],
        [5,6,7,8],
        [9,A,B,C],
        [D,E,F,0]
    ]
    => [
        [1,5,9,D,2,6,A,E],
        [3,7,B,F,4,8,C,0]
    ]
    avg = true, chunksize 2, 2
    => 
    [
        [1+2+5+6/2*2, 3+7+4+8/2*2, 9+A+D+E/2*2, B+C+F+0/2*2]
    ]

    Args:
        lums ([type]): [description]
        chunksize ([type]): [description]
        average (bool, optional): [description]. Defaults to True.

    Returns:
        [type]: [description]
    """    
    avg = lambda chunk : sum(chunk) / (chunksize[0] * chunksize[1])

    res = []

    y_out_of_bounds = False 
    x_out_of_bounds = False 

    row_index = 0
    xoffset = 0
    yoffset = 0
    xchunk, ychunk = chunksize

    while not y_out_of_bounds: 
        res.append([])
        try:
            while not x_out_of_bounds: 
                try: 
                    chunk = get_chunk((xoffset, yoffset), chunksize, lums)
                    if (average):
                        chunk = avg(chunk) 
                    res[row_index].append(chunk) 
                    xoffset += xchunk

                except IndexError:
                    # prepare next row 
                    res.append([])
                    xoffset = 0 
                    yoffset += ychunk
                    row_index += 1 
                    
                    # try next row 
                    chunk = get_chunk((xoffset, yoffset), chunksize, lums)
                    if(average):
                        chunk = avg(chunk)
                    res[row_index].append(chunk) 

                    # if we don't crash in l 94 cont in next row  
                    x_out_of_bounds = False 
                    
        except IndexError:
            y_out_of_bounds = True 
            res = res[:len(res)-1]
            
    return res 

def binarize(lums, compare = 128, invert=False):
    """ turns every value in lums to 1 or 0 depending on compare and invert

    Args:
        lums ([type]): array containing the values to binarize
        compare (int, optional): the value which decides whether 0 or 1. 
        Defaults to 128. x gt 128 => 1 else 0 
        invert (bool, optional): flips the comparison operator to leq. Defaults to False.

    Returns:
        [type]: [description]
    """    
    if invert: return list(map(lambda pixel : 1 if pixel <= compare else 0, lums))
    else: return list(map(lambda pixel : 1 if pixel > compare else 0, lums))

if __name__ == '__main__':
    import sys

    
    parser = ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('-i', default=False, action='store_true')
    parser.add_argument('-c', default=128, type=int)
    parser.add_argument('-f', default=2, type=int)

    args = parser.parse_args()

    # convert to black/white
    img = Image.open(args.filename).convert('LA')

    img = crop_even(img)

    x, y = img.size
    
    lum = map2D(list(map(lambda l : l[0], img.getdata())), x) 

    lum = compress2D(lum, tuple([args.f]*2))

    # compress without taking the average 
    lum = compress2D(lum, (2, 4), average=False)

    rowsz = len(lum[1])
    col_idx = 0  
    for row in lum: 
        for code in row: 
            col_idx += 1 
            if col_idx % rowsz == 0:
                print('\n', end='')
            else: 
                char = get_braille_char(binarize(code, args.c, args.i))
                print(char, end='')
