def strip_all(v):
    """
    Strips every string in array
    :param v: list/tuple of strings
    :return: list
    """
    return [s.strip() for s in v]

def split(inp,n):
    """
    Splits an input list into a list of lists.
    Length of each sub-list is n.
    :param inp:
    :param n:
    :return:
    """
    if len(inp) % n != 0:
        raise ValueError
    i = j = 0
    w = []
    w2 = []
    while i<len(inp):
        # print(i,j)
        if j==n:
            j = 0
            w2.append(w.copy())
            w = []
        w.append(inp[i])
        i += 1
        j += 1
    w2.append(w.copy())
    return w2

def get_range(s):
    """
    Takes a string of format [RANGE] and expands RANGE into the list of ints
    :param s:
    :return:
    """
    s_range = strip_all(s.split(','))
    v_res = []
    for s_element in s_range:
        if '-' in s_element:
            v = s_element.split('-')
            i = int(v[0])
            j = int(v[1])
            if i > j:
                raise SyntaxError
            for k in range(i,j+1):
                v_res.append(k)
        else:
            i = int(s_element)
            v_res.append(i)
    return v_res