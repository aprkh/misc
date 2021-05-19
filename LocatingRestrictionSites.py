################################################################################
# LocatingRestrictionSites.py
# Solves rosalind problem "Locating Restriction Sites":
# http://rosalind.info/problems/revp/
##
# Dependencies: TST.py - implementation of a ternary search trie.
################################################################################

import sys 
from Bio import SeqIO
from TST import TST
from collections import deque

BASES = {"A": 0, "C": 1, "G": 2, "T": 3}
COMPS = {"A": "T", "C": "G", "G": "C", "T": "A"}


def main():
    fname = "test.txt" 

    seq = read_input(fname)

    minlen = 4
    maxlen = 12

    locs = get_reverse_palindrome_locs(seq, minlen, maxlen)

    for key in locs:
        for val in locs[key]:
            print(key+1, val)

# ----------------------------------------------------------
# functions which compute locations of reverse palindromes.
# ----------------------------------------------------------
def get_reverse_palindrome_locs(seq, minlen, maxlen):
    """
    Returns the locations of all reverse palindromes in the 
    string of length between minlen and maxlen, inclusive. 

    A substring is a reverse palindrome if it is equal to its 
    reverse complement. 
    """
    # validate input parameters
    assert(0 < minlen <= maxlen)

    locmap = {}  # output variable

    k = minlen
    L = maxlen

    tst = create_trie(seq, k, L)
    locs = seek_reverse_palindrome(tst, seq, 0, k)
    
    if len(locs) > 0:
        locmap[0] = locs

    for j in range(1, len(seq)-k+1):
        tst = update_trie(tst, seq, j, k, L)
        locs = seek_reverse_palindrome(tst, seq, j, k)
        if len(locs) > 0:
            locmap[j] = locs

    return locmap

    
def seek_reverse_palindrome(tst, seq, index, k, d=COMPS):
    """
    Returns the length of any reverse palindromes starting 
    at the given index. 

    To find reverse palindromes, we look for the presence of 
    reverse complements to seq[index:index+k] in the search 
    trie, and if there do exist reverse complements, we 
    try to "extend" them to a full reverse palindrome. 

    d is the dictionary mapping nucleotides to complementary values. 
    """
    subseq = seq[index:index+k]
    rc_seq = rc(subseq)

    lengths = []
    i2_array = tst.get(rc_seq)

    if i2_array is None:
        return lengths 

    for i2 in i2_array:
        i2 += k - 1
        l = i2 - index + 1

        # ensure not too short 
        if l >= k:
            if is_reverse_palindrome(seq, index, i2, k, d):
                lengths.append(l)

    return lengths


def is_reverse_palindrome(seq, i1, i2, k, d):
    """
    Returns boolean indicating whether seq[i1:i2+1] is 
    a reverse palindrome. 
    """
    l = i2 - i1 + 1
    for i in range(l-k):
        if d[seq[i1]] != seq[i2]:
            return False
        i1 += 1
        i2 -= 1
    return True


# ----------------------------------------------------------
# functions for maintaining ternary-search-trie of k-mers
# ----------------------------------------------------------
def create_trie(seq, k, L):
    """
    Creates a ternary search trie consisting of the indices of 
    k-mers present in the L-prefix of seq; i.e., seq[0:L]

    Note: returns an empty trie if the sequence is too short 
    """
    n = len(seq)
    tst = TST()

    for i in range(L-k+1):
        if tst.contains(seq[i:i+k]):
            tst.get(seq[i:i+k]).append(i)
        else:
            tst.put(seq[i:i+k], deque([i]))

    return tst


def update_trie(tst, seq, index, k, L):
    """
    Updates the tst as we shift our sliding window down the sequence. 

    Assumes that we have a valid trie representing the k-mer positions for 
    seq[index-1: index+L-1].

    Updates to reflect k-mer positions for seq[index:index+L] (that is, deletes 
    seq[index-1:index+k-1] and adds seq[index+L-k:index+L]). The purpose of 
    deletion of the first k-mer index is to prevent the trie from getting too big 
    and taking too much memory - leaving that index in would not affect the 
    correctness of our solution. 

    If index is greater than len(seq)-L, then we do not need to add any more 
    k-mers, and simply delete old k-mers. Importantly, the index should never be
    greater than len(seq)-k. 
    """
    assert(0 < index <= len(seq)-k)
    
    # delete obsolete k-mer 
    old_kmer = seq[index-1:index+k-1]
    old = tst.get(old_kmer)
    if len(old) == 1:
        tst.delete(old_kmer) 
    else:
        old.popleft()

    # add new k-mer - if we are not at the end of the sequence 
    new_kmer = seq[index+L-k:index+L] 
    if len(new_kmer) >= k:
        new = tst.get(new_kmer) 
        if new is not None:
            new.append(new_kmer)
        else:
            tst.put(new_kmer, deque([index+L-k]))
    
    return tst

    
# ----------------------------------------------------------
# helper functions
# ----------------------------------------------------------
def rc(seq, d=COMPS):
    """
    Returns the reverse complement of seq. 
    """
    s = [None] * len(seq)
    for i in range(len(seq)):
        s[len(seq)-i-1] = d[seq[i]]
    return ''.join(s)


def comp(seq, d=COMPS):
    """
    Returns the complement of seq. 
    """
    s = [None] * len(seq)
    for i in range(len(seq)):
        try:
            s[i] = d[seq[i]]
        except KeyError:
            print("ERROR: invalid sequence passed in:", seq)
            print("Invalid key:", seq[i])
            sys.exit(1)
    return ''.join(s)


# ----------------------------------------------------------
# file I/O
# ----------------------------------------------------------
def read_input(fname):
    parser = SeqIO.parse(fname, "fasta")
    return str(next(parser).seq)


if __name__ == '__main__':
    main()
