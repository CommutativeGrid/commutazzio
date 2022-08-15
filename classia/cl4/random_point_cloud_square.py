#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 27 09:58:35 2021

@author: kasumi
"""
import numpy as np
import networkx as nx

class RandomPointCloudSquare:
    def __init__(self,orientation='f',dim=3):
        self.low_base = 50
        self.high_base = 100.1
        self.low_change = 10
        self.high_change = 15.1
        self.dim = dim
        self.orientation=orientation
        H=nx.DiGraph()
        #numeric keypad
        #789
        #456
        #123
        H.add_node(1, name="bottom_left") #bottom left
        H.add_node(3, name="bottom_right") #bottom right
        H.add_node(7, name="top_left") #top left
        H.add_node(9, name="top_right") #top right
        H.add_edge(1,7) # vertical arrow
        H.add_edge(3,9) # vertical arrow
        H.add_edges_from([(1,3),(7,9)])
        self.S=H #S stands for square
    
    @staticmethod
    def randomVectors(size,dim):
        return np.random.random([size,dim])
        
    def new_random_square(self):
        dim=self.dim
        pc_1_size=np.random.randint(self.low_base,self.high_base)
        pc_1=self.randomVectors(pc_1_size,dim)
        plus_3=self.randomVectors(np.random.randint(self.low_change,self.high_change),dim)
        plus_7=self.randomVectors(np.random.randint(self.low_change,self.high_change),dim)
        plus_9=self.randomVectors(np.random.randint(self.low_change,self.high_change),dim)
        pc_3=np.concatenate((pc_1,plus_3),axis=0)
        pc_7=np.concatenate((pc_1,plus_7),axis=0)
        pc_9=np.concatenate((pc_1,plus_3,plus_7,plus_9),axis=0)
        self.fill_all(*(pc_1,pc_3,pc_7,pc_9))
        
    def fill_all(self,pc_1,pc_3,pc_7,pc_9):
        values={1:{'pc':pc_1,'pc_size':len(pc_1)},
         3:{'pc':pc_3,'pc_size':len(pc_3)},
         7:{'pc':pc_7,'pc_size':len(pc_7)},
         9:{'pc':pc_9,'pc_size':len(pc_9)},
         }
        nx.set_node_attributes(self.S,values=values)
        if self.orientation == "b":
            H=nx.relabel_nodes(self.S,{1:3,3:1,7:9,9:7},copy=True)
            H.nodes[1].update({'name':'bottom_left'})
            H.nodes[3]['name']='bottom_right'
            H.nodes[7]['name']='top_left'
            H.nodes[9]['name']='top_right'
            self.S=H
            
            
        
    def fill_right(self,pc_1='random',pc_7='random'):
        """left column given, fill the right one"""
        dim = self.dim
        if type(pc_1) == str and type(pc_7) == str:
            pc_1 = self.randomVectors(np.random.randint(self.low_base,self.high_base),dim)
            plus_7=self.randomVectors(np.random.randint(self.low_change,self.high_change),dim)
            pc_7 = np.concatenate((pc_1,plus_7),axis=0)
            del(plus_7)
        if self.orientation == 'f':
            plus_3 = self.randomVectors(np.random.randint(self.low_change,self.high_change),dim) 
            plus_7 = [_ for _ in pc_7 if _ not in pc_1] # compute the difference between pc_7 and pc_1
            plus_9 = self.randomVectors(np.random.randint(self.low_change,self.high_change),dim)
            pc_3 = np.concatenate((pc_1,plus_3),axis=0)
            pc_9 = np.concatenate((pc_1,plus_3,plus_7,plus_9),axis=0)
            self.fill_all(*(pc_1,pc_3,pc_7,pc_9))
        elif self.orientation == 'b':
            self.__fill_left(pc_1,pc_7)
        else:
            raise NotImplementedError
        
        
        
    def __fill_left(self,pc_3='random',pc_9='random'):
        """right column given, fill the left one"""
        index_set_3=set(range(len(pc_3)))
        index_set_9=set(range(len(pc_9)))
        plus_9_to_3 = [_ for _ in pc_9 if _ not in pc_3] # compute the difference between pc_9 and pc_3

        minus_from_3 = np.random.choice(range(len(pc_3)),np.random.randint(self.low_change,self.high_change))
        indices_left=list(index_set_3-set(minus_from_3))
        minus_from_3_again = np.random.choice(indices_left,np.random.randint(self.low_change,self.high_change))
        minus_from_p_9_to_3 = np.random.choice(range(len(plus_9_to_3)),np.random.randint(self.low_change/3,self.high_change/3))
        index_set_1 = list(index_set_3-set(minus_from_3)-set(minus_from_3_again))
        index_set_7 = list(index_set_9-set(minus_from_3)-set(minus_from_p_9_to_3))
        pc_1=pc_3[index_set_1]
        pc_7=pc_9[index_set_7]
        self.fill_all(*(pc_1,pc_3,pc_7,pc_9))
        
    def info_pc(self,node):
        """
        Returns point cloud array and size
        """
        return {k:self.S.nodes[node][k] for k in {'pc','pc_size'} }
        
        
        
if __name__ == '__main__':
    a=RandomPointCloudSquare(orientation='b')
    a.fill_right()
    #a.new_random_square()
    
    
    
    
    
    