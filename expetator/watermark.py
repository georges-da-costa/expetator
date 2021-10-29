#TODO: put watermark detection at delta=0 if corr<.6

# For watermark detection
from sklearn import decomposition
import numpy as np


# for demo (to remove ?)
import matplotlib.pyplot as plt


# Tools for watermark detection
def df_to_vector(df):
    try:
        tmp = df.drop('#timestamp', axis=1)
    except:
        tmp = df
    pca = decomposition.PCA(n_components=1)
    pca.fit(tmp)
    x = pca.transform(tmp)
    return x.flatten()

def get_wm_ref(total_time=30, nb_steps=2, freq=10):
    low = int(total_time/(2*nb_steps+1))
    high = (total_time-low*(nb_steps+1))/nb_steps

    mark = np.array([])
    for _ in range(nb_steps):
        mark=np.append(mark, [-1]*int(low*freq))
        mark=np.append(mark, [1]*int(high*freq))
    mark=np.append(mark, [-1]*int(low*freq))
    return mark


def get_shift(dataframe, frequency=10, duration=30, backward=False):
    # Takes the best shift using a 10x frequency
    precision = 4
    timeframe = np.arange(0, duration, 1/(frequency*precision))

    # Gets the watermark on the timeframe
    watermark = get_wm_ref(freq=frequency*precision)

    # Gets the data regularly interpolated in the right window
    ts = dataframe['#timestamp'].to_numpy()
    if backward:
        pos_in_data = np.searchsorted(ts, max(ts)-duration )
        tmp_ts = ts[pos_in_data:]
        tmp_data = df_to_vector(dataframe[pos_in_data:])     
    else:
        pos_in_data = np.searchsorted(ts, min(ts)+duration )
        tmp_ts = ts[:pos_in_data+1]
        tmp_data = df_to_vector(dataframe[:pos_in_data+1])     
    
    data = np.interp(timeframe+min(tmp_ts), tmp_ts, tmp_data)
    
    deltamax = len(timeframe)//(2*precision)
    current = None
    res = None
    for delta in range(-deltamax, deltamax+1):
        if delta <= 0:
            coeff = np.corrcoef(data[:len(timeframe)+delta] ,
                                watermark[-delta:])[0][1]
        else:
            coeff = np.corrcoef(data[delta:] ,
                                watermark[:len(timeframe)-delta])[0][1]
        
        
        if current is None or abs(coeff) > current:
            current=abs(coeff)
            if backward:
                res = np.searchsorted(ts, max(ts)-duration+delta/(precision*frequency) ), coeff
            else:
                res = np.searchsorted(ts, min(ts)+duration+delta/(precision*frequency) ), coeff
        
            #print(delta, res)

    if current < .7:
        res = pos_in_data, 0
    
    return res

def remove_watermark(dataframe, frequency=10, duration=30):
    if len(dataframe) == 0:
        return dataframe
    delta_deb, conf_deb = get_shift(dataframe, frequency, duration)
    delta_fin, conf_fin = get_shift(dataframe, frequency, duration, backward=True)
    return dataframe[delta_deb:delta_fin+1].reset_index(drop=True)

def remove_watermark_blocks(block, frequency=10, duration=30):
    return [
        [
            remove_watermark(block[experiment][host], frequency, duration)
            for host in range(len(block[experiment]))
        ]
        for experiment in range(len(block))
    ]
        
## Tool for virtualisation

def demo_watermark_detection(focus, freq):
    df = focus.loc[:, focus.columns != '#timestamp']
    norm_focus=(df-df.min())/(df.max()-df.min())
    norm_focus['#timestamp'] = focus['#timestamp']
    fig, ax = plt.subplots()
    norm_focus.plot(x='#timestamp', figsize=(10,6), ax=ax)

    delta_deb, conf_deb = get_shift(focus, freq)
    delta_fin, conf_fin = get_shift(focus, freq, backward=True)

    # the actual data
    norm_focus[delta_deb:delta_fin+1].plot(x='#timestamp', linewidth=4, ax=ax)

    # common part of the watermark
    watermark_reference = (get_wm_ref(freq=freq)+1)/2
    nb_watermark = len(watermark_reference)

    #start
    w_start = min(focus[delta_deb:delta_fin+1]['#timestamp'])
    plt.plot(np.linspace(w_start-30, w_start-1/freq,len(watermark_reference)),
             watermark_reference)
    plt.vlines(w_start, 0, 1)
    plt.vlines(w_start-1/freq, 0, 1)

    #end
    w_end = max(focus[delta_deb:delta_fin+1]['#timestamp'])
    plt.plot(np.linspace(w_end + 1/freq, w_end+30,len(watermark_reference)),
             watermark_reference)
    plt.vlines(w_end, 0, 1)
    plt.vlines(w_end+1/freq, 0, 1)

    print(w_end-w_start)    
