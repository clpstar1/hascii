# -*- coding: utf-8 -*-

from PIL import ImageDraw



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
    # must be divisible by compression dims, x minimum of  4 because of braille conversion!

    comp_x, comp_y = (2,2)

    while x % comp_x != 0:
        x -= 1
        crop = True
    while y % comp_y != 0:
        y -= 1
        crop = True

    if crop:
        img = img.crop((0, 0, x, y))
    return img