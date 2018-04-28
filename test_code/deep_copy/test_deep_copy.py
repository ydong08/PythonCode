#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import copy

def deep_copy():
    #list
    lists = []
    lists.append('abc')
    lists.append(['123', '456', '789'])
    #list2 = lists
    #list2 = copy.copy(lists)
    list2 = copy.deepcopy(lists)
    print(lists)
    print(list2)

    list2[1].append('369')
    lists[1].append('uvw')
    print(lists)
    print(list2)

    list2 = lists[:]   #same as copy.deepcopy()
    list2.append('ghi')
    lists.append('jkl')
    print(lists)
    print(list2)
    print('\n')

    #dict
    dicts = {}
    dicts.update({1:'abc', 2:'def'})
    dicts.update({3:{'a':123, 'b':456}})
    #dicts2 = dicts
    #dicts2 = dicts.copy()
    #dicts2 = copy.copy(dicts)
    dicts2 = copy.deepcopy(dicts)
    print(dicts2)
    print(dicts)

    dicts2[1] = 'xyz'
    dicts[3].update({'c':789})
    print(dicts2)
    print(dicts)



def main():
    deep_copy()

if __name__ == '__main__':
    main()