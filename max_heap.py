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
        # pop_dict = {
        #     self.heap[hole][0]: self.heap[hole][1]
        # }
        # cur_album = self.heap[hole][0]
        cur_pop = self.heap[hole][1]


        parent_index = int((hole - 1) / 2)
        # parent_album = self.heap[parent_index][0]
        parent_pop = self.heap[parent_index][1]
        # parent_dict = self.heap[parent_index]
        # print(pop_dict['album popularity'])
        # print(parent_dict['album popularity'])
        while hole > 0 and cur_pop > parent_pop:
            temp = self.heap[hole]
            self.heap[hole] = self.heap[parent_index]
            self.heap[parent_index] = temp
            hole = parent_index
            parent_index = int((hole - 1) / 2)
            # parent_album = self.heap[parent_index][0]
            parent_pop = self.heap[parent_index][1]
            # self.heap[parent_index] = pop

    def print(self):
        print(self.heap)
