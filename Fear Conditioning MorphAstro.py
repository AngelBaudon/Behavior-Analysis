# -*- coding: utf-8 -*-
"""
Created on Thu Dec  8 16:36:19 2022

@author: Angel.BAUDON
"""


import pandas as pd, matplotlib.pyplot as plt, numpy as np, glob, scipy
from scipy.signal import find_peaks

file = r"C:\Angel.BAUDON\Exp\Comportement\Freezing\Choc dans Son\WT FEM PI.xlsx"
show_fig = True

data = pd.read_excel(file)
for col in data.columns:
    try: data.rename(columns={col:col.split('; ')[-1]}, inplace=True)
    except: pass

n_stage, sound_len = len(set(data['Stage'])), 20
Parameters = ('Freezing', 'PSTH Freezing')
Output = {x:[] for x in Parameters}

for animal in set(data['Animal']):
    datanimal = data[data['Animal'] == animal]
    
    Output_mouse = {x:[] for x in Parameters}
    plt.figure(figsize=(20,15)), plt.title(f'Mouse {animal}')
    for s, stage in enumerate(datanimal['Stage']):
        anistage = datanimal[datanimal['Stage'] == stage]
        
        X = {}
        for P in [x for x in set(anistage.columns)
                  if x not in ('Animal', 'Stage', 'Test')]:
            X[P] = np.asarray(anistage[P])[0]
        
        cs = X['Cage speaker : time active']
        gzz = X['Floor shock : number']
        freezing = X['Time freezing']

        
        CS, _ = find_peaks(np.diff(cs), height=.05, distance=30)
        Gzz, _ = find_peaks(gzz, height=.5, distance=30)


        Output_mouse['Freezing'].append([np.nanmean(freezing[int(cs):int(cs+sound_len)]) for cs in CS])
        

        red_cs = CS if 'Hab' in stage else CS[2:] if 'FC' in stage else CS[1:4]
        if not red_cs.size: red_cs = [30, 90, 150]
        
        Output_mouse['PSTH Freezing'].append([freezing[cs+1-sound_len :
                                                       cs+(sound_len*2)] for cs in red_cs])
        

        rows = n_stage+1
        plt.subplot(rows,1,s+1)
        plt.plot(freezing, zorder=1), plt.ylabel('Freezing')
        for idx in CS: plt.axvspan(idx, idx+sound_len, color='orange', alpha=.5, zorder=0)
        if len(Gzz): [plt.axvline(gz, color='r') for gz in Gzz]

    # for i, j in enumerate(Output_mouse['Freezing']):
    #     plt.subplot(rows, n_stage+1, n_stage*2+1)
    #     plt.ylim(0,1), plt.plot(j, c='r')
    # if not show_fig: plt.close()
    
    for k in Output.keys(): Output[k].append(Output_mouse[k])


col, n = len(set(data['Stage'])), len(set(data['Animal']))
val = [[x[y] for x in Output['Freezing']] for y in range(col)]
psth = [[np.nanmean(np.asarray(x[y]), axis=0) for x in Output['PSTH Freezing']]
        for y in range(col)]

plt.figure(figsize=(20, 10))
for i, (va, pst) in enumerate(zip(val, psth)):
    ar = np.zeros((n, max([len(x) for x in va])))
    ar[:], pst = np.nan, np.asarray(pst)
    
    for y, v in enumerate(va):
        for z, d in enumerate(v): ar[y,z] = d

    for a, (b, label) in enumerate(zip((ar, pst), ('Expositions', 'Seconds'))):
        #Handle NaNs
        b = b[~np.isnan(ar).any(axis=1)]
        
        mean, sem = np.nanmean(b, axis=0), scipy.stats.sem(b, axis=0)
        
        plt.subplot(2, col, col*a+i+1)
        plt.plot(mean, c='b')
        plt.fill_between(np.arange(len(mean)), mean-sem, mean+sem,
                          color='lightblue', alpha=0.25, zorder=1)
        
        plt.xlabel(label)
        plt.ylabel('Freezing') if not i else plt.ylabel('PSTH freezing')
        if a: plt.axvspan(sound_len, sound_len*2, color='orange', alpha=.5)
        plt.ylim(0,1)

plt.savefig(rf'{file[:-5]}.pdf')
if not show_fig: plt.close()

out = np.empty((50, animal))
out[:] = np.nan
for m, mouse in enumerate(Output['Freezing']): 
    data_mouse = [x for y in mouse for x in y]
    if len(data_mouse) != 50: data_mouse.append(np.nan)
    out[:,m] = data_mouse



df = pd.DataFrame(out)
writer = pd.ExcelWriter(f'{file[:-5]} analysis.xlsx')
df.to_excel(writer)
writer.save()