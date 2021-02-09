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
