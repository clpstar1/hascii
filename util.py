# -*- coding: utf-8 -*-

from PIL import Image, ImageFont, ImageDraw
import io
import pstats
import cProfile

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

def __get_chunk(offset, chunksize, arr):
    res = []
    xsize, ysize = chunksize
    xoff, yoff = offset
    for i in range(0, xsize):
        for j in range(0, ysize):
            res.append(arr[j+yoff][i+xoff])
    return res 

def binarize(lums, compare = 128, invert=False):
    if invert: return list(map(lambda pixel : 1 if pixel <= compare else 0, lums))
    else: return list(map(lambda pixel : 1 if pixel > compare else 0, lums))

def print_luminance_map(luminance2D, compare_value, invert):
    rowsz = len(luminance2D[1])
    col_idx = 0  
    for row in luminance2D: 
        for code in row: 
            col_idx += 1 
            if col_idx % rowsz == 0:
                print('\n', end='')
            else: 
                char = get_braille_char(binarize(code, compare_value, invert))
                print(char, end='')




def draw_out_img(charmap2D, out_img:Image, row_height, font):
    imgDraw = ImageDraw.Draw(out_img)
    i = 0
    for row in charmap2D:
        h = i * row_height
        imgDraw.text((0, h), row, font=font, fill='white')
        i+=1


def get_img_dims(luminance2D, font, compare_value, invert):
    h = len(luminance2D[0])
    width, single_row_height = font.getsize('⣿' * h)
    return (width, single_row_height)



