############################################################
# fitted_align.py
##
# uses numpy matrix rather than graph. this presents a
# challenge - must find a way to store path information
# information that would normally be given by incoming and
# outgoing edges.
############################################################

import numpy as np
import heapq

LEFT = -1
DIAG = 0
UP = 1
TO_START = -5
TO_END = 5


def main():
    fname = "dataset_248_5 (12).txt"
    with open(fname, 'rt') as f:
        v = f.readline().strip()
        w = f.readline().strip()
    (v_aln, w_aln), score = fitted_align(v, w, Score())

    with open("out.txt", 'wt') as out:
        print(score, v_aln, w_aln, sep='\n', file=out)


def fitted_align(v, w, score, sigma=-1, epsilon=-1):
    """
    returns a fitted alignment of strings v and w. shorter string fit to longer.
    score - object x with method x.score(v[i], w[j]) for indices i and j 
    sigma - gap-open penalty
    epsilon - gap-extension penalty (not implemented for now)
    """
    if len(w) < len(v):
        v, w = w, v
    m = len(v) + 1
    n = len(w) + 1

    # alignment and backtrack matrices
    a = np.zeros((m, n), dtype="int64")
    b = np.zeros((m, n), dtype="int64")

    # for first row, all nodes have edges back to the start node
    for i in range(1, n):
        b[0, i] = TO_START
    for i in range(1, m):
        a[i, 0] = a[i - 1, 0] + sigma
        b[i, 0] = UP

    # collect top-scoring node on bottom row
    top_node = tuple([None])

    # fill in remainder of alignment and backtrack matrix
    # fill in remainder of matrix
    for i in range(1, m):
        for j in range(1, n):
            vchar = v[i - 1]
            wchar = w[j - 1]

            from_above = a[i - 1, j] + sigma
            from_left = a[i, j - 1] + sigma
            from_diag = a[i - 1, j - 1] + score.score(vchar, wchar)

            max_score = max(from_above, from_left, from_diag)

            back = None
            if max_score == from_left:
                back = LEFT
            elif max_score == from_above:
                back = UP
            else:
                back = DIAG

            a[i, j] = max_score
            b[i, j] = back

            # store top-scoring bottom-node
            if i == m - 1:
                if not top_node[0] or top_node[0] < max_score:
                    top_node = (max_score, i, j)

    # backtrack through graph - first go to top-scoring region
    i = top_node[1]
    j = top_node[2]
    score = top_node[0]
    v_aln = []
    w_aln = []

    while i > 0 or j > 0:
        if b[i, j] == TO_START:
            break
        elif b[i, j] == LEFT:
            j -= 1
            v_aln.append('-')
            w_aln.append(w[j])
        elif b[i, j] == UP:
            i -= 1
            v_aln.append(v[i])
            w_aln.append('-')
        else:
            i -= 1
            j -= 1
            v_aln.append(v[i])
            w_aln.append(w[j])

    v_out = ''.join(v_aln)[::-1]
    w_out = ''.join(w_aln)[::-1]
    return (w_out, v_out), score


class Score():

    def __init__(self, fname="PAM250.txt"):
        pass

    def score(self, v, w):
        return 1 if v == w else -1


if __name__ == "__main__":
    main()
