#! /usr/bin/python3

import os
import sys
import pandas as pd

def get_nb_freq(file_list):
    m_size = 0
    representative = ''

    for filename in file_list:
        stat = os.stat(filename)
        if stat.st_size > m_size:
            m_size = stat.st_size
            representative = filename

    data = pd.read_csv(representative, sep=' ')
    return len(set(data['fmax']))

def main():
    print(get_nb_freq(sys.argv[1:]))

if __name__ == '__main__':
    main()

