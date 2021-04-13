

if __name__ == '__main__':
    import sys
    import subprocess
    
    parser = ArgumentParser()
    parser.add_argument('filenames', nargs='+')
    parser.add_argument('-i', default=False, action='store_true')
    parser.add_argument('-c', default=128, type=int)
    parser.add_argument('-f', default=2, type=int)
    parser.add_argument('-d', default=False, action='store_true')

    args = parser.parse_args()

    img_buffer = []
    img_index = 0
    BUFFER_SIZE = 1

    IMG_POS = 0
    FILE_NAME_POS = 1

    for filename in args.filenames:
        
        if args.d:
            f, t, m = convert_debug(filename, args)
        else:
            f, t, m = convert(filename, args)

        if img_index % BUFFER_SIZE == 0:
            for img, out_file_name in img_buffer:
                img.save(out_file_name, 'PNG')
            img_buffer = []

        img_buffer.append((Image.new('LA', (t[0], t[1]*len(m)), 'black'), f'f_{img_index:04}.png'))
        draw_out_img(m, img_buffer[img_index % BUFFER_SIZE][IMG_POS], t[1], f)
        img_index += 1

        # print_luminance_map(lum2D_compressed, avg_lum, args.i)
    for img, out_file_name in img_buffer:
            img.save(out_file_name, 'PNG')

            