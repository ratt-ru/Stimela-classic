# -*- coding: future_fstrings -*-
class dismissable:
    '''
    Wrapper for optional parameters to stimela
    Initialize with val == None to force stimela to skip
    parsing parameter.
    '''

    def __init__(self, val=None):
        self.__val = val

    def __call__(self):
        return self.__val
