from functools import reduce

class BrailleMapper:

    def __init__(self):
        self.symbol_cache = {}

    def map_codes_to_symbols(self, luminance2D, compare_value, invert):

        res2 = []
        for row in luminance2D:
            res = []
            for code in row:
                binarized = binarize(code, compare_value, invert)
                as_tuple = tuple(binarized)
                if as_tuple in self.symbol_cache:
                    braille = self.symbol_cache[as_tuple]
                else:
                    braille = get_braille_char(binarized)
                    self.symbol_cache[as_tuple] = braille

                res.append(braille)
            res2.append(res)
        

        return [reduce(lambda a,b: a+b, row) for row in res2]


def get_braille_char(arr):
    """
    takes an array of bits and returns the
    braille representation of that array.
    the highest bit represents the upper left dot.
    breaks into a new column after
    the 4th bit. array MUST be 8 bits long
    e.g
    [0,0,0,1,1,1,1,1,1] => ⣰

    [0,0,0,0,1,1,1,1] => []

    Args:
        arr ([type]): array representing the braille

    Returns:
        [type]: the unicode braille char
    """

    def swap(x, y):
        tmp = arr[x]
        arr[x] = arr[y]
        arr[y] = tmp

    swap(3, 4) 
    swap(4, 5)
    swap(5, 6)
    # 10240 is the base of the braille unicode block
    out_char = chr(arr_to_bin(arr) + 10240)
    return out_char


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

def binarize(lums, compare=128, invert=False):
    """ turns every value in lums to 1 or 0 depending on compare and invert

    Args:
        lums ([type]): array containing the values to binarize
        compare (int, optional): the value which decides whether 0 or 1.
        Defaults to 128. x gt 128 => 1 else 0
        invert (bool, optional): flips the comparison operator to leq.
        Defaults to False.

    Returns:
        [type]: [description]
    """
    if invert:
        return list(map(lambda pixel: 1 if pixel <= compare else 0, lums))
    else:
        return list(map(lambda pixel: 1 if pixel > compare else 0, lums))


def get_padding(a, b):
    if b > a:
        raise ValueError

    if a == b:
        return 0


    diff = 0
    while a % b != 0:
        diff += 1
        a += 1

    return diff

def skip_padding(pixels, number_of_rows, bytes_per_row, padding):
    res = bytearray()
    prev_width = 0
    width = bytes_per_row
    # cut off padding after each row.
    for _ in range(0, number_of_rows):
        res += pixels[prev_width: width - padding]
        prev_width += bytes_per_row 
        width += bytes_per_row
    
    return res

def cat_rows(charmap2D):
    img_str = ''
    for row in charmap2D:
        img_str += row + '\n'
    
    return img_str

