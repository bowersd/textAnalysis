####
##
#Edited on May 15, 2013 from source implementing the Needleman-Wunsch algonrithm for global sequence alignment by "vmandal"
#Source originally from http://www.codesofmylife.com/2011/04/10/needleman-wunsch-algorithm-for-global-sequence-alignment-in-python/
#Re-edited April 2021
##
####

import sys
    
def read_similarity_matrix(fileName):
    '''
    Read a tab-delimited similarity matrix and return the similarity map of
    all the combinations of the bases.
    The file must be delimited by whitespace.
    The first row and column must be the categories that the similarity matrix
    evaluates.
    '''
    with open(fileName) as fileIn:
        # turn the file into a list of lists
        similarityMatrix = [line.split() for line in fileIn]
        # extract the categories we are working with
        categories = similarityMatrix[0]
        # turn the list of lists into a dictionary of category pair, violation mappings
        similarityMatrixMap = dict()
        for i in range(len(categories)):
            base1 = categories[i]
            for j in range(len(categories)):
                base2 = categories[j]
                # because the file looks like:
                #   A   B
                #A  1   -1
                #B  -1  1
                # split() has made 'A' be the zeroth element
                # so we need to add 1 to the list indices
                similarityMatrixMap[base1 + base2] = int(similarityMatrix[i+1][j+1])
    return similarityMatrixMap

def make_id_matrix(seq1, seq2):
    # change counts as -1
    # identity counts as 1
    basicCategories = []
    for char in seq1+seq2:
        if char not in basicCategories: basicCategories.append(char)
    # making the dictionary of category pair, violation mappings as above
    similarityMatrixMap = dict()
    for i in range(len(basicCategories)):
        base1 = basicCategories[i]
        for j in range(len(basicCategories)):
            base2 = basicCategories[j]
            if base1 == base2: similarityMatrixMap[base1+base2] = 1
            else: similarityMatrixMap[base1+base2] = -1
    return similarityMatrixMap

    
def score_strings(seq1, seq2, gapPenalty, similarityMatrix):
    '''
    This function creates the alignment score matrix.
    seq1 : reference sequence
    seq2 : other sequence
    gapPenalty : gap penalty (-1 is a good default)
    similarityMatrix : similarity matrix (use read_similarity_matrix() or make_id_matrix().)
    '''
    rows = len(seq1) + 1
    cols = len(seq2) + 1
    matrix = [[0 for i in range(cols)] for j in range(rows)]
    # filling in the first row and column of the alignment matrix
    for i in range(rows): matrix[i][0] = i * gapPenalty 
    for j in range(cols): matrix[0][j] = j * gapPenalty
    # filling in the remainder of the alignment matrix.
    for i in range(1, rows):
        for j in range(1, cols):
            mtch = matrix[i - 1][j - 1] + similarityMatrix[seq1[i - 1] + seq2[j - 1]]
            delete = matrix[i - 1][j] + gapPenalty
            insert = matrix[i][j - 1] + gapPenalty
            matrix[i][j] = max(mtch, delete, insert)
    return matrix


def track_back(matrix, seq1, seq2, gapPenalty, similarityMap):
    '''
    Tracks back to make tuple of aligned strings.
    See score_strings() for documentation of arguments.
    '''
    alignedSeq1 = ''
    alignedSeq2 = ''
    i = len(seq1)
    j = len(seq2)
    while i > 0 and j > 0:
        score = matrix[i][j]
        diagScore = matrix[i - 1][j - 1]
        upScore = matrix[i][j - 1]
        leftScore = matrix[i -1][j]
        if score == diagScore + similarityMap[seq1[i - 1] + seq2[j - 1]]:
            alignedSeq1 = seq1[i - 1] + alignedSeq1
            alignedSeq2 = seq2[j - 1] + alignedSeq2
            i -= 1
            j -= 1
        elif score == leftScore + gapPenalty:
            alignedSeq1 = seq1[i - 1] + alignedSeq1
            alignedSeq2 = '_' + alignedSeq2
            i -= 1
        elif score == upScore + gapPenalty:
            alignedSeq1 = '_' + alignedSeq1
            alignedSeq2 = seq2[j - 1] + alignedSeq2
            j -= 1
        else:
            # this isn't a very informative error message, consider fixing
            sys.stderr.write('Not Possible')
    while i > 0:
        alignedSeq1 = seq1[i - 1] + alignedSeq1
        alignedSeq2 = '_' + alignedSeq2
        i -= 1
    while j > 0:
        alignedSeq1 = '_' + alignedSeq1
        alignedSeq2 = seq2[j - 1] + alignedSeq2
        j -= 1
    return (alignedSeq1, alignedSeq2)

def align(seq1, seq2, gapPenalty, similarityMap):
    return track_back(score_strings(seq1, seq2, gapPenalty, similarityMap), seq1, seq2, gapPenalty, similarityMap)

if __name__ == "__main__":
    pass
    #print(track_back(score_strings(seq1, seq2, gapPenalty, similarityMap), seq1, seq2, gapPenalty, similarityMatrix))

