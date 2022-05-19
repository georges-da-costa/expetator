#! /usr/bin/python3

import sys
import pandas as pd

def clean_csv(filename, nb):

    df = pd.read_csv(filename, sep=' ', )

    # remove the last incomplete experiment
    last = (len(df)//nb)*nb
    df = df[:last]

    # remove complete experiment is the monitoring failed
    for bloc_id in range(len(df)//nb-1,-1, -1):
        for idx in range(nb):
            tmp = df.iloc[bloc_id*nb+idx]
            if min(tmp[10:]) <= -1:
                df = df.drop( range(bloc_id*nb, (bloc_id+1)*nb) )
                break
                

    df.to_csv(filename[:-4]+"_cleaned.csv", sep=' ', index=False)

def main():
    if len(sys.argv) != 3:
        print("usage %s filename expe_size\nwhere expe_size is the number of experiment for one experimental set")
    
    else:
        clean_csv(sys.argv[1], int(sys.argv[2]))

if __name__ == '__main__':
    main()

    
