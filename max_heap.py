from nodes import Node
import pandas as pd


'''
Heap
constructor: 
insert: add a node to the heap
  a. percolate up/down
print: print the heap
'''


class Heap(object):
    heap = []

    def __init__(self, data):
        self.heap = []
        if data.size < 2:
            raise Exception('need more than titles in the dataFrame')
        else:  # get the top of the df and assign to root

            for index, row in data.iterrows():
                self.insert(row=row)

    def insert(self, row):
        self.heap.append(row)
        hole = len(self.heap) - 1
        self.percolate_up(hole)

    def percolate_up(self, hole):
        cur_pop = self.heap[hole][1]

        parent_index = int((hole - 1) / 2)
        parent_pop = self.heap[parent_index][1]

        while hole > 0 and cur_pop > parent_pop:
            temp = self.heap[hole]
            self.heap[hole] = self.heap[parent_index]
            self.heap[parent_index] = temp

            hole = parent_index
            parent_index = int((hole - 1) / 2)
            parent_pop = self.heap[parent_index][1]

    def print(self):
        height = len(self.heap)  # the amount of nodes in the heap
        branch_l = "/"           # there are height - 1 branches in a heap. left, then right branch order
        space = " "
        branch_r = "\\"
        for line in range(1, height * 8):
            self.symbol(' ', (-1 * line) + (height * 8))
            print(self.heap[line - 1])
            self.symbol('/', line)
            print()
            pass

    def symbol(self, character, amount):
        for i in range(amount):
            print(character, end="")

    def detail(self, info):
        for album in range(len(info)):
            print(info[album])
