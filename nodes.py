import pandas as pd


class Node(object):
    data: dict
    left = None
    right = None

    def __init__(self, data, left=None, right=None):
        self.data = data
        self.left = left
        self.right = right

    def toString(self):
        return f"[{self.data}]"
