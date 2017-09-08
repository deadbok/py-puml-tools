import ast
import logging

LOGGER = logging.getLogger()

def global_func(arg1, arg2, arg3=None):
    """A simple function at module level"""

class A(object):
    def __init__(self, name, details={}, **kwargs):
        """Constructor"""
        self.name = name
        self.details = details

    @staticmethod
    def cls_meth():
        return "Some setting"

    def meth1(self, arg1, arg2="default", *args, **kwargs):
        """This method uses many sorts or args"""
        pass

class Child(A):
    clsvar = 1
    def meth1(self, arg1, arg2, arg3=888):
        super().meth1(arg1, arg2, arg3, arg4="extra")
        return True

class MyVisitor(ast.NodeVisitor):
    pass

from abc import ABCMeta, abstractmethod
class C:
    __metaclass__ = ABCMeta
    @abstractmethod
    def my_abstract_method(self, arg1):
        pass
