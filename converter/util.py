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
    if x % 2 != 0:
        x -= 1
        crop = True
    if y % 2 != 0:
        y -= 1
        crop = True

    if crop:
        img = img.crop((0, 0, x, y))
    return img


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


def draw_out_img(charmap2D, out_image, font):
    draw = ImageDraw.Draw(out_image)
    image_str = ''
    i = 0
    for row in charmap2D:
        nrow = row
        print(nrow)
        image_str += (nrow + '\n')
        i += 1

    draw.multiline_text((0, 0), image_str, font=font, fill='white')


def get_img_dims(rowsz, font):
    width, single_row_height = font.getsize('⣿' * rowsz)
    return (width, single_row_height)
