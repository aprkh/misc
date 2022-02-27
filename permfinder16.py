#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  5 10:09:09 2019

@author: hampster
"""
# now supports gzip files

import argparse
import time
from Bio import SeqIO
import gzip
#%%
class Permutation():
    '''
    Class which conveniently stores relevant permutation information, including
    whether or not permutation occurs in sense or antisense strand.
    '''
    def __init__(self, loc, match, header, sense=True):
        self.loc = loc
        self.match = match
        self.contig = None
        self.start = None
        self.end = None
        self.header = header
        self.sense = sense
    
    def get_contig(self, seq, up, down, whole):
        if whole:
            self.start = 0
            self.end = len(seq)
        elif self.sense:
            self.start = max(self.loc-up, 0)
            self.end = min(self.loc+down, len(seq))
        else:
            self.start = max(self.loc-down, 0)
            self.end = min(self.loc+up, len(seq))
        self.contig = seq[self.start:self.end]
        
    def update_header(self):
        if self.sense:
            suffix = 'loc={}-{}(+)|match={}'.format(self.start+1, 
                          self.end+1, self.match)
        else:
            suffix = 'loc={}-{}(-)|match={}'.format(self.start+1, 
                          self.end+1, self.match)
        self.header = '|'.join((self.header, suffix))
        
    def update_match(self, num):
        while self.match not in permutation_extender(self.match[:num],
                                                     len(self.match)):
            self.match = self.match[:-1]
            
    def get_filter_stat(self, n):
        contig_loc = self.contig.find(self.match)
        return 'Q' not in self.contig[contig_loc-n:contig_loc+n+len(self.match)]
        

#%% main fuction
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-pattern', type=str, dest='pattern', required=True)
    parser.add_argument('-infile', type=str, dest='infile', required=True)
    parser.add_argument('-minlength', type=int, dest='minlength', default=-1)
    parser.add_argument('-maxlength', type=int, dest='maxlength', default=-1)
    parser.add_argument('--whole_contig', action='store_true')
    parser.add_argument('-upstream', type=int, dest='up', default=100)
    parser.add_argument('-downstream', type=int, dest='down', default=400)
    parser.add_argument('-outfile', dest='output', type=str, required=True)
    parser.add_argument('-table', dest='out_table', type=str, default='')
    parser.add_argument('--mask', action='store_true')
    parser.add_argument('-filter', type=int, dest='filter', default=0)
    parser.add_argument('--gzip', action='store_true')
    parser.set_defaults(func=run)
    args = parser.parse_args()
    args.func(args)
    

def run(args):
    st = time.time()
    all_perms = []
    with open_file(args.infile, args.gzip) as f:
        for record in SeqIO.parse(f, 'fasta'):
            record_sequence = str(record.seq)
            record_header = record.description
            if args.mask or args.filter > 0:
                record_sequence = mask_telomeres(record_sequence, args.pattern)
            all_perms.extend(permutation_search(record_sequence, args.pattern, args.up, 
                                                args.down, record_header, args.whole_contig,
                                                args.minlength, args.maxlength))
    all_perms = filter_perms(all_perms, args.filter)
    if len(args.out_table) > 0:
        write_table_output(args, all_perms)
    cands = write_fasta_output(args.output, all_perms)  
    print('Time taken:', time.time()-st)
    print('There were {} candidates found in this search'.format(cands))

#%% utility functions
def open_file(fname, cond):
    if cond:
        import gzip
        return gzip.open(fname, 'rt')
    return open(fname, 'rt')

def comp_base_dict_constructor():
    """
    Generates a dictionary containing complementary base pairs for standard bases of A, C, G, or T, ambiguous N nucleotides, and some other base notations such as K, M, R, and Y. Lower case nucleotides are supported by the returned dictionary. Outputs: python dictionary. 
    """
    comp_bases = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C', 'N': 'N', 'Y': 'R', 'R': 'Y', 'M': 'K', 'K': 'M'}
    for k, v in tuple(comp_bases.items()):
        comp_bases[k.lower()] = v.lower()
    return comp_bases

def complement(seq, comp_bases=None, reverse=False): 
    """
    Generates a complementary strand if DNA to a provided DNA string. If specified, this function will return a reverse complement. Inputs: seq(string), comp_bases (python dictionary), reverse (boolean).
    """
    # make dictionary of complementary bases if one is not already provided
    if not comp_bases: 
        try:
            comp_bases = comp_base_dict_constructor()
        except NameError:
            print('''Please provide a dictionary containing all DNA bases and their complements in the sequence to be examined. A helper function which contains nucleotide sequences containing  A, C, G, T, and N (upper or lower case) can be found in the same file this function was imported from: dnautil.py. To import the function, use the following code: from dnautil import comp_base_dict_constructor.''') # make complementary DNA strand         
    comp_strand = ''.join([comp_bases[base] for base in seq])
    if reverse:
        return comp_strand[::-1]
    return comp_strand

def permutations_generator(seq):
    """
    A more general function compared with initial_TR_perm_generator found in perm_finder2.py. Generates permutations of a pattern. For example, a 5-nt pattern TTAGG will return the following list of permutations: [TTAGG, TAGGT, AGGTT, GGTTA, GTTAG]. Inputs: seq (string), num (integrer). Outputs: permutations (list).
    """
    permlis = list()
    permlis.append(seq)
    for i in range(1, len(seq)): 
        permlis.append(seq[i:] + seq[:i])
    return permlis    


def permutation_extender(pattern, n):
    """
    Generates permutations of a pattern, then extends them to length n.
    Uses function permutations_generator found in module dnautil.py
    Inputs: pattern (string)
    Outputs: permutations extended to length n (list)
    """
    perm_lis = permutations_generator(pattern)
    ext_perm_lis = list()
    for perm in perm_lis:
        perm = perm * (n // len(perm))
        ext_perm_lis.append(''.join((perm, perm[:n-len(perm)])))
    return ext_perm_lis

#%% permutation search
def permutation_search(sequence, pattern, up, down, header, whole, minlen, maxlen):
    """
    Searches for permutations of the pattern of length n+2:2n+1 for specified
    pattern and its reverse complement. Outputs list of permutations (class). 
    """
    # k = len(pattern)+2, k_long = 2(len(pattern))+1
    if minlen < 0:
        k = len(pattern)+2; k_long = (2*len(pattern))+1
    else:
        k = minlen
    
    if maxlen < 0:
        k_long = (2*len(pattern)) + 1
    else:
        k_long = maxlen
    
    # telomere pattern indicates possible TR alignment domain in anti-sense strand
    comp_pattern = pattern 
    pattern = complement(pattern, reverse=True)
    # k = len(pattern)+2, k_long = 2(len(pattern))+1
    # k = len(pattern)+2; k_long = (2*len(pattern))+1
    
    perms, long_perms = (permutation_extender(pattern, k),
                         permutation_extender(pattern, k_long))

    revperms, long_revperms = (permutation_extender(comp_pattern, k),
                               permutation_extender(comp_pattern, k_long))
    # handle for lower case characters
    seq = sequence.upper()
    # different rule for bad bases: if region has both G and C in
    # subsequence, skip (for telomere repeat TTAGG(G))
    n = len(seq)
    i = 0
    
    #output list
    permlist = list()
    
    while i <= n-k+1:
        subseq = seq[i:i+k].upper()
        
        if subseq in perms:
            if seq[i:i+k_long] not in long_perms \
            and seq[i+1-k_long:i+1] not in long_perms:
                match = seq[i:i+k_long]
                loc = i
                perm = Permutation(loc, match, header)
                perm.get_contig(sequence, up, down, whole)
                perm.update_header()
                permlist.append(perm)
            # Increment i to skip over permutation.            
            i += k_long
            continue 
        
        elif subseq in revperms:
            if seq[i:i+k_long] not in long_revperms \
            and seq[i+1-k_long:i+1] not in long_revperms:
                match = seq[i:i+k_long]
                loc = i
                perm = Permutation(loc, match, header, sense=False)
                perm.get_contig(sequence, up, down, whole)
                perm.update_header()
                permlist.append(perm)
            # Increment i to skip over permutation.            
            i += k_long
            continue
        i += 1
    return permlist


def mask_telomeres(seq, pattern):
    comp_pattern = complement(pattern, reverse=True)
    mask_num = 0

    for pat in (pattern*3, comp_pattern*3):
        last_hit = 0
        seqlis = []
        while True:
            hit = seq[last_hit:].find(pat)
            if hit == -1:
                seqlis.append(seq[last_hit:])
                break
            seqlis.append(seq[last_hit:last_hit+hit])
            seqlis.append('Q'*len(pat))
            last_hit += hit + len(pat)
            mask_num += 1
        seq = ''.join(seqlis) 
    return ''.join(seqlis)


def filter_perms(permlis, n):
    if n > 0:
        return [perm for perm in permlis if perm.get_filter_stat(n)]
    return permlis
    
#%%
def write_fasta_output(file_name, permlist):
    total_ct = 0
    with open(file_name, 'w') as file_handle:
        for perm in permlist:
            # parse sequence into chuncks of 60
            seq = []
            for i, c in enumerate(perm.contig):
                if i % 60 == 0 and i > 0:
                    seq.append('\n')
                seq.append(c)
            fasta_sequence = ''.join(seq)
        
            file_handle.write('>{0}\n{1}\n'.format(perm.header, fasta_sequence))
            total_ct += 1
    
    return total_ct


def write_table_output(args, permlist):
    import pandas as pd
    
    data = {'Contig': [],
        'Putative Template': [],
        'Template Length': [],
        'Contig Start': [],
        'Contig End': [],
        'Strand': []}
    
    for perm in permlist:
        perm.update_match(len(args.pattern))
        data['Contig'].append(perm.header)
        data['Putative Template'].append(perm.match)
        data['Template Length'].append(len(perm.match))
        data['Contig Start'].append(perm.start+1)
        data['Contig End'].append(perm.end+1)
        if perm.sense:
            data['Strand'].append('+')
        else:
            data['Strand'].append('-')

    df = pd.DataFrame(data)
    df = df.set_index('Contig')

    if '.xlsx' in args.out_table:
        df.to_excel(args.out_table)
    else:
        df.to_csv(args.out_table)
#%% run function

if __name__ == "__main__":
    main()
