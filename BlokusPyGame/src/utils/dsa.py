# Sometimes python doesn't have built-in data structures or algorithms that can make things easier for you so 
# you have to develop those methods yourself. 
# Below is the following data structures and algorithms used given to you like an utility file

from heapq import heapify, heappush, heappushpop, nlargest

class MaxHeap():
    def __init__(self, top_n):
        self.h = []
        self.length = top_n
        heapify( self.h)
        
    def add(self, element):
        if len(self.h) < self.length:
            heappush(self.h, element)

        elif len(self.h) > self.length:
            heappushpop(self.h, element)
            
    def getTop(self):
        return nlargest(self.length, self.h)


if __name__ == "__main__": # Sometimes I like to test my code

    #Test max heap class
    possible_moves: list[int] = []
    maxheap = MaxHeap(30)
    maxheap.add(3); maxheap.add(4); maxheap.add(1)
    max_h = maxheap.getTop()
    print(max_h)

    size_h21 = 20
    max_h21 = MaxHeap(size_h21)
    import random 
    rints = [random.randint(1, 50) for _ in range(100)]

    for item in rints:
        max_h21.add(item)
    top_max = max_h21.getTop()
    print(top_max)
    
    
    
