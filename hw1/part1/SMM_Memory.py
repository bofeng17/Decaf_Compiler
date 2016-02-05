# """Memory models for SMM"""
class Stack:
    """Stack for SMM, support methods: pop(), push(val)"""
    def __init__(self):
        self.__data = []

    def pop(self):
        _ret = self.__data.pop()
        return _ret;

    def push(self, val):
        self.__data.append(val)

    def getStack(self):
        return self.__data

class Store:
    """Store for SMM, support methods: store(addr, val), load(addr)"""
    def __init__(self):
        self.__data = {}

    def store(self, addr, val):
        self.__data[addr] = val

    def load(self, addr):
        _ret = self.__data[addr]
        return _ret;
    def getStore(self):
        return self.__data





