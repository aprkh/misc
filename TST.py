############################################################
# TST.py
# Implementaion of ternary-search-trie. 
############################################################

import sys 
import random


def main():
    testTST()


class Node:

    def __init__(self, c=None):
        self.c = c
        self.val = None
        self.left = None 
        self.mid = None
        self.right = None

class TST:

    def __init__(self):
        self.root = Node()

    # ------------------------------------------------------
    # Inserting into trie
    # ------------------------------------------------------
    def put(self, key, val):
        """
        Inserts key into trie and associates key with value. 
        """
        assert(isinstance(key, str))
        if len(key) >= 1:
            index = 0
            self.root.mid = self.put_recursive(self.root.mid, key, val, index)

    def put_recursive(self, node, key, val, index):
        if node is None:
            node = Node(key[index])
        if key[index] < node.c:
            node.left = self.put_recursive(node.left, key, val, index) 
        elif key[index] > node.c:
            node.right = self.put_recursive(node.right, key, val, index) 
        elif index < len(key) - 1:
            node.mid = self.put_recursive(node.mid, key, val, index+1)
        else:
            node.val = val
        return node

    # ------------------------------------------------------
    # Retrieving from trie
    # ------------------------------------------------------
    def get(self, key):
        """
        Returns value associated with key, returns None if key 
        is not associated with any value in the trie. 
        """
        if self.root.mid is None:  # trie is empty 
            return None
        index = 0
        return self.get_recursive(self.root.mid, key, index)
    
    def get_recursive(self, node, key, index):
        if node is None:  # key is not in tree
            return None 
        if key[index] < node.c:
            return self.get_recursive(node.left, key, index)
        elif key[index] > node.c:
            return self.get_recursive(node.right, key, index)
        elif index < len(key) - 1:
            return self.get_recursive(node.mid, key, index+1)
        else:
            return node.val

    # ------------------------------------------------------
    # Deleting from trie
    # ------------------------------------------------------
    def delete(self, key): 
        """
        Deletes the given key from a trie. 
        """
        index = 0
        self.root.mid = self.delete_recursive(self.root.mid, key, index)
    
    def delete_recursive(self, node, key, index):
        if node is None:  # key is not in tree
            return None 
        if key[index] < node.c:
            node.left = self.delete_recursive(node.left, key, index) 
        elif key[index] > node.c:
            node.right = self.delete_recursive(node.right, key, index) 
        elif index < len(key) - 1:
            node.mid = self.delete_recursive(node.mid, key, index+1)
        else:
            node.val = None

        # if there are no more nodes down the middle path, check if we can delete this node. 
        # we can delete the middle node if there are no left or right paths as well as the 
        # middle path. 
        if node.val is None:
            if node.mid is None:
                if node.left is None: 
                    return node.right  # could be None, should be correct either way
                elif node.right is None: # we know that node.left is not None
                    return node.left

        return node


# ----------------------------------------------------------
# test functions
# ----------------------------------------------------------

def testTST(ntrials=1000, Llim=100):
    """
    Performs ntrials random operations in parallel in python dictionary and
    TST, in order to ensure that TST is implemented properly.

    Keys are no longer than Llim. 
    """
    A = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+<>?:\"';"

    arrkeys = list()

    delkeys = set()

    test_d = {}
    tst = TST()

    # a key is deleted with probability 10%
    for j in range(ntrials):
        u = random.uniform(0,1)
        L = random.randint(1, Llim)
        n = random.randint(-Llim, Llim)
        if u < 0.50:
            if len(arrkeys) > 0:
                i = random.randint(0, len(arrkeys)-1)
                s = arrkeys[i] 
                arrkeys.pop(i)
            else:
                s = random_string(L, A)
            if s in test_d:
                del test_d[s]
            tst.delete(s)

            delkeys.add(s)

            assert(s not in test_d and tst.get(s) is None)

        s = random_string(L, A)
        tst.put(s, n)
        test_d[s] = n

    del s
    for s in test_d:
        print(s, test_d[s], tst.get(s), s in delkeys)
        assert(test_d[s] == tst.get(s))

    print("all tests passed!", len(delkeys))
            


def random_string(L, alphabet):
    """
    Creates a random string of length L from a alphabet. 
    """
    k = len(alphabet)
    s = [None] * L 
    for i in range(L):
        u = random.uniform(0, 1)
        j = random.randint(0, k-1)
        if u < 0.5:
            s[i] = alphabet[j]
        else:
            s[i] = alphabet[j].lower()
    return ''.join(s)


if __name__ == '__main__':
    main()
