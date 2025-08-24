import ctypes

def make_array(n):
    return (n * ctypes.py_object)()

class ArrayDeque:
    INITIAL_CAPACITY = 8

    def __init__(self):
        self.data = make_array(ArrayDeque.INITIAL_CAPACITY)
        self.num_of_elems = 0
        self.front_ind = None
        self.back_ind = None

    def __len__(self):
        return self.num_of_elems

    def isEmpty(self):
        return self.num_of_elems == 0

    def enqueueFirst(self, elem):
        if self.num_of_elems == len(self.data):
            self.resize(2 * len(self.data))
        if self.isEmpty():
            self.data[0] = elem
            self.front_ind = 0
            self.back_ind = 0
            self.num_of_elems = 1
        else:
            self.front_ind = (self.front_ind - 1) % len(self.data)
            self.data[self.front_ind] = elem
            self.num_of_elems += 1

    def enqueueLast(self, elem):
        if self.num_of_elems == len(self.data):
            self.resize(2 * len(self.data))
        if self.isEmpty():
            self.data[0] = elem
            self.front_ind = 0
            self.back_ind = 0
            self.num_of_elems = 1
        else:
            self.back_ind = (self.back_ind + 1) % len(self.data)
            self.data[self.back_ind] = elem
            self.num_of_elems += 1

    def dequeueFirst(self):
        if self.isEmpty():
            raise Exception("Queue is empty")
        value = self.data[self.front_ind]
        self.data[self.front_ind] = None
        self.front_ind = (self.front_ind + 1) % len(self.data)
        self.num_of_elems -= 1
        if self.isEmpty():
            self.front_ind = None
            self.back_ind = None
        elif self.num_of_elems < len(self.data) // 4:
            self.resize(len(self.data) // 2)
        return value

    def dequeueLast(self):
        if self.isEmpty():
            raise Exception("Queue is empty")
        value = self.data[self.back_ind]
        self.data[self.back_ind] = None
        self.back_ind = (self.back_ind - 1) % len(self.data)
        self.num_of_elems -= 1
        if self.isEmpty():
            self.front_ind = None
            self.back_ind = None
        elif self.num_of_elems < len(self.data) // 4:
            self.resize(len(self.data) // 2)
        return value

    def first(self):
        if self.isEmpty():
            raise Exception("Queue is empty")
        return self.data[self.front_ind]

    def last(self):
        if self.isEmpty():
            raise Exception("Queue is empty")
        return self.data[self.back_ind]

    def resize(self, new_cap):
        old_data = self.data
        new_data = make_array(new_cap)
        old_ind = self.front_ind
        for new_ind in range(self.num_of_elems):
            new_data[new_ind] = old_data[old_ind]
            old_ind = (old_ind + 1) % len(old_data)
        self.data = new_data
        self.front_ind = 0
        self.back_ind = self.front_ind + self.num_of_elems - 1
