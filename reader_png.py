def read_png():
    
    i = 0
    
    check_end = False 
    end_reached = False 

    PNG = bytearray()

    END_STR = list(b'DNE')

    READ_CRC = 4

    img_index = 0

    for byte in sys.stdin.buffer.read():

        PNG.append(byte)
        
        byte = bytes([byte])

        # initiate end check
        if byte == b'I':
            check_end = True 
            continue

        # check next char if previous was binary I  
        if check_end:
            compare = END_STR.pop()
            check_end = bytes([compare]) == byte
            
            # regen stack if comparison failed.
            if not check_end:
                END_STR = list(b'DNE')
            
            if len(END_STR) == 0:
                # IEND was consecutively read.
                check_end = False
                end_reached = True 
                END_STR = list(b'DNE')

        if end_reached:
            if READ_CRC == 0:
                f, t, m = convert_from_bin(PNG, {})
                img = Image.new('L', (t[0], t[1]*len(m)), 'black')
                draw_out_img(m, img, t[1], f)
                img.save()
                PNG = bytearray()
                end_reached = False
                READ_CRC = 4
            else: 
                READ_CRC -= 1 