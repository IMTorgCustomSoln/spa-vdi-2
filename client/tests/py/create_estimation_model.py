#!/usr/bin/env python3
"""
Module Docstring


event states:
* progress
* load
* loadend
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"


import pandas as pd
import numpy as np
import plotnine as p9
from sklearn.linear_model import QuantileRegressor

import argparse
from pathlib import Path
import json


def main(args):
    """ Main entry point of the app """
    paths = Path(args.input_dir).glob('**/*')
    logs_paths = [x for x in paths if ((x.is_file()) and not ('DS_Store' in x.name))]
    file_events = []

    for batch_idx, log in enumerate(logs_paths):
        with open(log, 'r') as f:
            while line := f.readline():
                ln = line.rstrip()

                time = int( ln.split(':')[0] )
                event = ln.split('event ')[1].split(' with')[0].replace("'",'')
                record = {
                    'time': time,
                    'batch_idx': batch_idx,
                    'batch_start_time': 0,
                    'batch_duration': 0,
                    'batch_file_count': 0,
                    'batch_size': 0,
                    'file_idx':  int( ln.split('file ')[1].split(' -')[0] ),
                    'file_path': ln.split(' underwent')[0].split(' -')[1].strip(),
                    'file_start_time': 0,
                    'file_duration': 0,
                    'file_size': 0,
                    'event': event,
                    'bytes_transferred': int( ln.split(' bytes')[0].split(' with')[1] )
                }
                file_events.append( record )

    df_raw = pd.DataFrame(file_events)
    print(f'df shape: {df_raw.shape}')
    df_raw['idx'] = df_raw['batch_idx'].astype('str') +'-'+ df_raw['file_idx'].astype('str')
    df_raw.sort_values(by=['idx','time'], inplace=True)

    batch_events_mod = []
    for batch in df_raw['batch_idx'].unique():
        batch_records = df_raw[df_raw['batch_idx']==batch]
        file_count = batch_records['file_idx'].unique().__len__()
        batch_records['batch_file_count'] = file_count

        total_bytes = batch_records[batch_records['event']=='loadend']['bytes_transferred'].sum()
        batch_records['batch_size'] = total_bytes

        startTime = batch_records['time'].min()
        batch_records['batch_start_time'] = startTime
        batch_records['batch_duration'] = batch_records['time'] - batch_records['batch_start_time']
        recs = batch_records.to_dict(orient='records')
        batch_events_mod.extend( recs )

    df_batch = pd.DataFrame(batch_events_mod)
    assert df_batch.shape == df_raw.shape
    
    file_events_mod = []
    for file in df_batch['idx'].unique():
        file_records = df_batch[df_batch['idx']==file]
        size = file_records['bytes_transferred'].max()
        file_records['file_size'] = size

        startTime = file_records['time'].min()
        file_records['file_start_time'] = startTime
        file_records['file_duration'] = file_records['time'] - file_records['file_start_time']
        recs = file_records.to_dict(orient='records')
        file_events_mod.extend( recs )

    df = pd.DataFrame(file_events_mod)
    assert df.shape == df_raw.shape

    if args.plots:
        plot = (p9.ggplot(df, p9.aes('file_duration', 'bytes_transferred', color='file_size'))
         + p9.geom_point()
         + p9.stat_smooth(method="lm")
         + p9.facet_wrap("~batch_idx")
         + p9.scales.scale_x_log10()
         + p9.scales.scale_y_log10()
         )
        plot.save(filename = './tests/py/plot-1.png', height=5, width=8, units='in', dpi=100)

        plot = (p9.ggplot(df[df['event'].isin(['progress','load','loadend'])], p9.aes('batch_duration', 'file_duration', color='file_size'))
         + p9.geom_point()
         + p9.stat_smooth(method="lm")
         + p9.facet_wrap("~event")
         + p9.scales.scale_x_log10()
         + p9.scales.scale_y_log10()
         )
        plot.save(filename = './tests/py/plot-2.png', height=5, width=8, units='in', dpi=100)

        plot = (p9.ggplot(df[df['event'].isin(['progress','load','loadend'])], p9.aes('bytes_transferred', 'file_duration', color='file_size'))
         + p9.geom_point()
         + p9.stat_smooth(method="lm")
         + p9.facet_wrap("~event")
         + p9.scales.scale_x_log10()
         + p9.scales.scale_y_log10()
         )
        plot.save(filename = './tests/py/plot-3.png', height=5, width=8, units='in', dpi=100)

        plot = (p9.ggplot(df[df['event'].isin(['progress','load','loadend'])], p9.aes('batch_file_count', 'batch_duration', color='file_size'))
         + p9.geom_point()
         + p9.stat_smooth(method="lm")
         + p9.facet_wrap("~event")
         + p9.scales.scale_x_log10()
         + p9.scales.scale_y_log10()
         )
        plot.save(filename = './tests/py/plot-4.png', height=5, width=8, units='in', dpi=100)

    if args.estimate_model :
        tmp = df[df['event'].isin(['progress','load','loadend'])]

        cols1 = ['batch_duration']
        y1 = tmp[cols1]
        y2 = tmp['file_duration'].to_frame()
        y2.columns = cols1
        y3 = pd.concat([y1, y2])
        y = np.log10( y3[cols1[0]].to_numpy(copy="deep") )

        cols1 = [ 'event', 'batch_size', 'batch_file_count']
        X1 = tmp[cols1]
        X1['type'] = 'batch'
        cols2 = ['event', 'file_size']
        X2 = tmp[cols2]
        X2['batch_file_count'] = 1
        X2.columns = cols1
        X2['type'] = 'single'
        X3 = pd.concat([X1, X2])
        colnames = ['event','size', 'file_count', 'type']    #final column names
        X3.columns = colnames
        cols = ['size', 'file_count']
        X = np.log10( X3[cols].to_numpy(copy="deep") )

        df_mod = X3
        df_mod['duration'] = y3['batch_duration']

        plot = (p9.ggplot(df_mod[df_mod['event'].isin(['progress','load','loadend'])], p9.aes('size','duration', color='file_count'))
         + p9.geom_point()
         + p9.stat_smooth(method="lm")
         + p9.facet_wrap("~event")
         + p9.scales.scale_x_log10()
         + p9.scales.scale_y_log10()
         )
        plot.save(filename = './tests/py/plot-5.png', height=5, width=8, units='in', dpi=100)

        solver = "highs"
        quantiles = [.5, .75, .95]
        coefs = {}
        preds = {}
        for quantile in quantiles:
            qr = QuantileRegressor(quantile=quantile, alpha=0, solver=solver)
            f = qr.fit(X, y)
            coef_dict = dict(zip(cols, f.coef_.tolist()))
            coefs[str(quantile)] = coef_dict
            y_pred = f.predict(X)
            MAD = np.mean( np.abs(np.exp(y_pred) - np.exp(y)) )    #apply exp to get interpretable result
            preds[str(quantile)] = MAD.tolist()

        results = {
            'coefs': coefs,
            'preds': preds
            }
        with open('./tests/py/results.json', 'w') as file:
            file.write(json.dumps(results))


        




if __name__ == "__main__":
    """ This is executed when run from the command line """
    parser = argparse.ArgumentParser()

    # Required positional argument
    parser.add_argument("--input_dir", help="input directory for log files")
    parser.add_argument("--plots", default=True, help="produce all plots")
    parser.add_argument("--estimate_model", default=True, help="output results.json file")

    # Specify output of "--version"
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__))

    args = parser.parse_args()
    main(args)