from __future__ import print_function

import re
import copy

#placeholders
class placeholder:
    def __init__(self, val):
        if val not in ["input", "msfile", "output"]:
            raise ValueError("Only accepts input, output or msfile for placeholder argument")
        self.__val = val

    def __call__(self):
        return self.__val

    def __get__(self):
        return self.__val

    def __repr__(self):
        return "Placeholder(type {})".format(self.__val)

class pathformatter:
    '''
    Wrapper for path variables that need further expansion
    to include base directories
    expect:
        pattern: of the format (({})?[\s\S-[{}]]*)*, {} indicate placeholders where
                 paths are to be inserted. \{ and \} escapes these groups
        *args: of special string types input, output and
               msfile. Will attempt to replace placeholders in order
               of *args specification
    Example:
        ...
        {
            'model': pathformatter("MODEL_DATA:{}/mod2.lsm:{}/mod3.DicoModel", "output", "input")
        }...
        This will create placeholders for output and input on the second and third files
        respectively.
    '''
    def __init__(self, val=None, *args):
        if not isinstance(val, str):
            raise ValueError("argument must be of type string")
        self.__val = val
        self.__args = list(map(lambda x: placeholder(x), args[::-1]))

    def __call__(self):
        """ returns list with mixed value types str, input, msdir or output """
        args = list(copy.deepcopy(self.__args))
        exp = re.compile(r"((?P<R>{})?(?P<T>(?!{})[\S\s]))")
        expr_list = []
        esc = re.compile(r"(\\{|\\})").split(self.__val) + [None]
        for v, delim in zip(esc[::2],
                            esc[1::2]):
            for m in exp.finditer(v):
                if m.groupdict()["R"] is not None:
                    if len(args) == 0:
                        raise RuntimeError("cannot replace format string - not enough arguments specified")
                    expr_list.append(args.pop())
                    expr_list.append(m.groupdict()["T"])
                else:
                    if len(expr_list) > 0:
                        expr_list[-1] += m.groupdict()["T"]
                    else:
                        expr_list.append(m.groupdict()["T"])
            if delim:
                if len(expr_list) > 0:
                     expr_list[-1] += delim[-1]
                else:
                    expr_list.append(delim[-1])
        if len(args) != 0:
            raise RuntimeError("could not replace all arguments")
        return expr_list

if __name__ == "__main__":
    p = pathformatter("MODEL_DATA+-{}/bla\{ab\}.DicoModel@{}/poly.reg:{}/abc.lsm",
                  "output",
                  "output",
                  "input")
    print(p())
