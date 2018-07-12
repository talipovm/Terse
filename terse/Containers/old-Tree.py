def flatten(v):
    out = []
    for item in v:
        if isinstance(item,list):
            out.extend(flatten(item))
        else:
            out.append(item)
    return out

def within(v, key):
    if not isinstance(v,list):
        return (v.key==key)
    if isinstance(v[0],list):
        for item in v:
            if not within(item,key):
                return False
    else:
        for i in v:
            if i.key==key:
                return True
        else:
            return False

def cut_list(v, key):
    res = []
    res2 = []
    for i in v:
        if i.key==key:
            if res2:
                res.append(res2)
            res2 = [i,]
        else:
            res2.append(i)
    res.append(res2)
    return res

def cut_tree(v, key):
    if isinstance(v[0],list):
        return [cut_tree(item,key) for item in v]
    else:
        return cut_list(v,key)

def print_tree(v,prefix=''):
    for item in v:
        if isinstance(item,list):
            print(prefix+'List:')
            print_tree(item,prefix+'  ')
        else:
            print(prefix+str(item))

if __name__ == '__main__':
    class Z():
        def __init__(self, key, data):
            self.key = key
            self.data = data

        def __str__(self):
            return "%s: %s" % (self.key, self.data)

    v = [Z('a',1),Z('b',2),Z('c',3), Z('b',10),Z('c',11),Z('d',12)]

    print_tree(cut_list(v,'a'))

    res = cut_list(v,'b')
    v2 = [[res,res],res]
    print_tree(v2)

    [within(x,'e') for x in res]

    print_tree(res)

    print_tree(cut_tree(res,'d'))