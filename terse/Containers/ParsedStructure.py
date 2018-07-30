from Top import Top
from copy import deepcopy
import collections
import re

import logging
log = logging.getLogger(__name__)

if __name__ == "__main__":
    import sys
    sys.path.append('..')

class ParsedElement(Top):
    def __init__(self, key=None, data=None):
        super().__init__()
        self.key = key
        self.data = data

    def __str__(self,prefix=''):
        return "%s%s: %s" % (prefix, self.key, self.data)

    def get_columns(self, new_keys):
        columns = zip(*self.data)
        return [ParsedElement(k,v) for k,v in zip(new_keys,columns)]



class ParsedContainer(Top):
    def __init__(self, key = 'Main', data=None):
        super().__init__()
        self.key = key
        self.aggregate_name = collections.defaultdict(dict)
        if data is None:
            self.data = list()
        else:
            self.data = data

    def flatten(self):
        """
        :return: List
        """
        out = []
        for item in self.data:
            if isinstance(item,ParsedContainer):
                out.extend(item.flatten())
            else:
                out.append(item)
        return out

    def append(self,*args):
        self.data.append(*args)

    def get_item(self, key):
        return [i for i in self.flatten() if i.key==key]

    def find_items(self,pattern):
        sre = re.compile(pattern)
        return [i for i in self.flatten() if sre.search(i.key)]

    def find_keys(self,pattern):
        sre = re.compile(pattern)
        return [i.key for i in self.flatten() if sre.search(i.key)]

    def get_value(self, key):
        return [i.data for i in self.flatten() if i.key==key]

    def get_last_item(self, key):
        item = self.get_item(key)
        if item:
            if isinstance(item,(list,tuple)):
                return item[-1]
            else:
                return item
        else:
            return None

    def last_value(self, key):
        out = self.get_last_item(key)
        if out is None:
            return None
        if isinstance(out.data,str):
            return out.data.strip()
        return out.data

    def add_latest_rec(self, old_key, new_key):
        if not self.data:
            return
        last_i = None
        for i in self.data:
            if i.key==old_key:
                last_i = i
        if last_i is not None:
            new_i = deepcopy(last_i)
            new_i.key = new_key
            self.append(new_i)

    def conditionally_add(self, old_key, new_key, old_value=None, new_value=None):
        if not self.data:
            return
        for (i,d) in enumerate(self.data):
            if d.key!=old_key:
                continue
            if (old_value is None) or (d.data==old_value):
                if new_value is not None:
                    new_data = new_value
                else:
                    new_data = deepcopy(d.data)
                if new_key==old_key:
                    d.data = new_value
                else:
                    z = ParsedElement(key=new_key, data=new_data)
                    self.data.insert(i+1,z)

    def edit_nonempty_rec(self, old_key=None, new_key=None, new_value=None):
        if not self.data:
            return
        for (i,d) in enumerate(self.data):
            if d.key==old_key and d.data != 'empty':
                if new_value is not None:
                    new_data = new_value
                else:
                    new_data = deepcopy(d.data)
                z = ParsedElement(key=new_key, data=new_data)
                self.data.insert(i+1,z)

    def to_empty(self, old_key=None, new_key=None):
        if not self.data:
            return
        v = self.get_item(new_key)
        if v and [i.key for i in v if i.key!='empty']:
            return
        self.conditionally_add(old_key,new_key)

    def join_unique(self, old_key=None, new_key=None):
        if not self.data:
            return
        v = ParsedElement(key=new_key,data=list())
        for i in self.data:
            if i.key==old_key and not i.data in v.data:
                v.data.append(i.data)
        self.append(v)

    def group_container_by_key(self, key, new_key=None, before=True):
        self.aggregate_name[new_key][key]=before

    def separate(self, new_key=None):
        if not new_key in self.aggregate_name:
            return [self]

        res = ParsedContainer()
        res2 = ParsedContainer(key=new_key)
        for i in self.data:  # loop over ParseElements
            for key,before in self.aggregate_name[new_key].items():
                if i.key != key:
                    continue
                if before:
                    if res2: res.append(res2)
                    res2 = ParsedContainer(key=new_key, data=[i, ])
                else:
                    res2.append(i)
                    res.append(res2)
                    res2 = ParsedContainer(key=new_key)
                    break
            else:
                res2.append(i)
        if res2: res.append(res2)
        return res

    def separate_columns(self, old_key, new_keys):
        for (i,item) in enumerate(self.data):
            if item.key!=old_key:
                continue
            z = self.data.pop(i)
            for pe in z.get_columns(new_keys):
                self.data.insert(i,pe)