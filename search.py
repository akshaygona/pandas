class Node():
    def __init__(self, key):
        self.key = key
        self.values = []
        self.left = None
        self.right = None
        
    def __len__(self):
        size = len(self.values)
        if self.left != None:
            size += self.left.__len__()
        if self.right != None:
            size += self.right.__len__()
        return size
    
    def lookup(self, key):
        if self.key == key:
            return self.values
        elif key < self.key and self.left != None:
            return self.left.lookup(key)
        elif key > self.key and self.right != None:
            return self.right.lookup(key)
        else:
            return list()
        
class BST():
    def __init__(self):
        self.root = None
    def add(self, key, val):
        if self.root == None:
            self.root = Node(key)

        curr = self.root
        while True:
            if key < curr.key:
                if curr.left == None:
                    curr.left = Node(key)
                curr = curr.left
            elif key > curr.key:
                if curr.right == None:
                    curr.right = Node(key)
                curr = curr.right
            else:
                assert curr.key == key
                break
        curr.values.append(val)
        
    def __dump(self, node):
        if node == None:
            return
        self.__dump(node.left)      
        print(node.key, ":", node.values)
        self.__dump(node.right)       

    def dump(self):
        self.__dump(self.root)
    
    def __getitem__(self, i):
        return self.root.lookup(i)
    