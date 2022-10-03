################################################################################
# pdf_merge.py
# usage: python pdf_merge.py FILE1 FILE2 ... -o OUTPUT
################################################################################

from PyPDF2 import PdfFileMerger
import sys

USAGE = "usage: python pdf_merge.py FILE1 FILE2 ... -o OUTPUT"

# parse arguments
OUTPUT_FLAG = -1
try:
    assert(len(sys.argv) > 1)
    OUTPUT_FLAG = sys.argv.index('-o')
    assert(OUTPUT_FLAG > 1)
except(ValueError, AssertionError):
    sys.exit(USAGE)


def main():
    pdf_merger = PdfFileMerger()
    index = 1
    try:
        while index < OUTPUT_FLAG:
            pdf_merger.append(sys.argv[index])
            index += 1
        with open(sys.argv[OUTPUT_FLAG + 1], 'wb') as out:
            pdf_merger.write(out)
            print('wrote file:', sys.argv[OUTPUT_FLAG + 1])
    except FileNotFoundError:
        print("invalid file name:", sys.argv[index])
        sys.exit("aborting!")

    print('job completed successfully. exiting!')


if __name__ == '__main__':
    main()
