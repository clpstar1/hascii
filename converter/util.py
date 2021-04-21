# -*- coding: utf-8 -*-

from PIL import ImageDraw


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