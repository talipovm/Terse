from Top import Top
import logging
log = logging.getLogger(__name__)
from copy import deepcopy

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


class ParsedContainer(Top):
    def __init__(self, key = 'Main', data=None):
        super().__init__()
        self.key = key
        self.aggregate_name = None
        if data is None:
            self.data = []
        else:
            self.data = data

    def __bool__(self):
        return bool(self.data)

    def __str__(self,*args):
        return self.print_tree_rec(self)

    def __contains__(self, key):
        return key in self.keys()

    def append(self,*args):
        self.data.append(*args)

    def keys(self):
        return [x.key for x in self.flatten()]

    def get_item(self, key):
        return [i for i in self.flatten() if i.key==key]

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

    def int_values(self):
        """
        :return: a dictionary of keys with integer values
        """
        d = {}
        for assigned_element in self.data:
            try:
                d[assigned_element.key] = int(assigned_element.data) # will overwrite old data
            except (ValueError,TypeError):
                continue
        return d

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

    def print_tree_rec(self, v, prefix=''):
        if isinstance(v,ParsedContainer):
            s = '%sContainer %s:\n' % (prefix, v.key)
            for item in v.data:
                s += self.print_tree_rec(item, prefix + '  ')
            return s
        else:
            return "%s%s\n" % (prefix,v)

    """
    def get_last(self, key):
        latest_item = None
        for item in self.flatten():
            if key == item.key:
                latest_item = item
        return latest_item
    """

    def add_latest_rec(self, old_key, new_key):
        if not self.data:
            return
        if isinstance(self.data[0],ParsedContainer):
            for item in self.data:
                item.add_latest_rec(old_key=old_key, new_key=new_key)
        else:
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
        if isinstance(self.data[0],ParsedContainer):
            for item in self.data:
                item.conditionally_add(old_key, new_key, old_value, new_value)
            return
        for i in self.data:
            if i.key!=old_key:
                continue
            if (old_value is None) or (i.data==old_value):
                i.key = new_key
                if new_value is not None:
                    i.data = new_value

    def edit_nonempty_rec(self, old_key=None, new_key=None):
        if not self.data:
            return
        if isinstance(self.data[0],ParsedContainer):
            for item in self.data:
                item.edit_nonempty_rec(old_key, new_key)
        else:
            for i in self.data:
                if i.key==old_key and i.data != 'empty':
                    i.key = new_key
                    #if new_value is not None:
                    #    i.data = new_value

    def join_unique(self, old_key=None, new_key=None):
        if not self.data:
            return
        if isinstance(self.data[0],ParsedContainer):
            for item in self.data:
                item.join_unique(old_key, new_key)
        else:
            v = ParsedElement()
            v.key = new_key
            v.data = []

            for i in self.flatten():
                if i.key==old_key and not i.data in v.data:
                    v.data.append(i.data)
            self.append(v)

    def group_plain_container_by_key(self, key, new_key=None, before=True):
        res = ParsedContainer()
        res2 = ParsedContainer(key=new_key)
        for i in self.data: # loop over ParseElements
            if i.key==key:
                if before:
                    if res2: res.append(res2)
                    res2 = ParsedContainer(key=new_key, data=[i,])
                else:
                    res2.append(i)
                    res.append(res2)
                    res2 = ParsedContainer(key=new_key)
            else:
                res2.append(i)
        if res2: res.append(res2)
        self.aggregate_name = new_key.strip().lower()
        self.data = res.data

    def group_container_by_key(self, key, new_key=None, before=True):
        """
        Internally rearranges the .data
        :param key:
        :param new_key:
        :return:
        """
        if not self.data:
            return
        if isinstance(self.data[0],ParsedContainer): # Container data are assumed to be of the same type
            [item.group_container_by_key(key, new_key, before=before) for item in self.data]
        else:
            self.group_plain_container_by_key(key=key, new_key=new_key, before=before)

if __name__ == "__main__":
    from Settings import Settings
    from Top import Top
    Top.settings = Settings()
    Top.settings.detailed_print = True

    Z = ParsedElement
    v = ParsedContainer(data=[Z('a', '  abc '), Z('b', 2), Z('c', 3), Z('b', 10), Z('c', 11), Z('d', 12)])
    print(v)

    v.group_container_by_key('b', new_key='JOB')
    #v.group_plain_container_by_key('b', new_key='IRC')

    v.group_container_by_key('c', new_key='IRC')
    v.group_container_by_key('d', new_key='opt')
    #print(v.get_last('c'))


    #print(ParsedContainer(data=[i for i in v.flatten()]))

    #print([item.segment_contains('c') for item in v.data])
