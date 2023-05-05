# -*- coding: utf-8 -*-
"""
Created on Wed Nov  2 17:13:33 2022

@author: Angel.BAUDON
"""

import numpy as np, pandas as pd, matplotlib.pyplot as plt, scipy, seaborn as sns, scipy


ko = r"C:\Angel.BAUDON\Exp\Comportement\Sucrose\Sucrose GFAP OTR KO 3 au 5 octobre 2022.xlsx"
ctrl = r"C:\Angel.BAUDON\Exp\Comportement\Sucrose\Sucrose Ctrl 20 au 22 janvier 2023.xlsx"
labels = ("KO", "Ctrl")
pref = {}

for data, name in zip((ko, ctrl), labels):
    
    df = pd.read_excel(data)
    
    raw = df.iloc[1:,2:8].astype('float64').to_numpy()
    
    diff_water_d1, diff_sucr_d1 = raw[:,0] - raw[:,2], raw[:,1] - raw[:,3]
    diff_water_d2, diff_sucr_d2 = raw[:,2] - raw[:,4], raw[:,3] - raw[:,5]
    
    
    pref_d1 = (diff_sucr_d1/(diff_sucr_d1+diff_water_d1))*100
    pref_d2 = (diff_sucr_d2/(diff_sucr_d2+diff_water_d2))*100
    
    pref[name] = (pref_d1 + pref_d2) / 2

plt.figure()
means = [np.nanmean(pref[x]) for x in labels]
sems = [scipy.stats.sem(pref[x]) for x in labels]
plt.bar((0,1), means, yerr=sems, capsize=5)
plt.xticks((0,1), labels)
# plt.savefig(rf'{folder}\Histo distrib {key}.pdf'), plt.close()