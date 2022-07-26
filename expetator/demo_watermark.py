#! /usr/bin/python3

import expetator.monitoring_csv as monitoring_csv
import expetator.monitoring_list as monitoring_list
import expetator.watermark as watermark
import sys
import pandas as pd
import matplotlib.pyplot as plt
import json

if __name__ == '__main__':
    if len(sys.argv) != 3 or not sys.argv[1] in ['csv', 'list']:
        print("""Usage :
%s csv file.csv

or

%s list file.list
""")
        sys.exit(0)

    filename = sys.argv[2]
    if sys.argv[1] == 'csv':
        
        a = monitoring_csv._read_csv(filename)
        watermark.demo_watermark_detection(a, 10)
        plt.show(block=True)


    if sys.argv[1] == 'list':

        with open(filename) as f_id:
            data = json.load(f_id)

            for name, timestamps, power in data:

                df = pd.DataFrame([timestamps, power]).transpose()
                df.columns = ["#timestamp", "Values"]

                watermark.demo_watermark_detection(df, 10)
                plt.show(block=True)



        
                
