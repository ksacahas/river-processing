import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm, gaussian_kde
import os


def bimodality_significance(unknown_path, controls_path, n_meanders):
    sample_densities_to_save = [2, 3, 4, 5, 10, 20, 30, 40, 50, 100, 200, 250]
    
    if n_meanders==0:
        unknown = pd.read_csv(unknown_path)
        controls = pd.read_csv(controls_path)

        n_controls = controls['name'].nunique()
        names_controls = controls['name'].unique()

        p_values = []
        dir_path = os.path.dirname(unknown_path)
        file_name = os.path.splitext(os.path.basename(unknown_path))[0]
        file_stem = file_name.replace("_bimodality_results.csv", "")

        unknown_g = unknown.groupby('samples')['bimodal'].sum().reset_index() # in %

        samples = pd.Series(list(set(unknown_g['samples']).intersection(controls['samples'])))
        
        for d in samples:
            unknown_d_bimodal = unknown_g[unknown_g['samples']==d]['bimodal'].iloc[0]
            controls_d = controls[controls['samples']==d]
            controls_d_bimodal = []
            for name in names_controls:
                num_bimodal = controls_d[controls_d['name']==name]['bimodal'].sum()
                controls_d_bimodal.append(num_bimodal)
                
            
            kde = gaussian_kde(controls_d_bimodal, bw_method='scott')
            xs = np.linspace(0,100,num=1000)

            p_value_kde = (1 - kde.integrate_box_1d(-np.inf, unknown_d_bimodal))    
            p_values.append([d, p_value_kde])

        df = pd.DataFrame(p_values, columns=['samples', 'p-value'])
        df.to_csv(os.path.join(dir_path, file_stem+'_p_values.csv'))
        

    else:
        unknown = pd.read_csv(unknown_path)
        controls = pd.read_csv(controls_path)

        n_controls = controls['name'].nunique()
        names_controls = controls['name'].unique()

        if len(names_controls) <= 1:
            raise ValueError("Control data set must contain more than 1 river.")

        p_values = []
        dir_path = os.path.dirname(unknown_path)
        file_name = os.path.basename(unknown_path)
        file_stem = file_name.replace("_bimodality_results.csv", "")

        unknown['sample density'] = unknown['samples']/n_meanders

        unknown_g = unknown.groupby('sample density')['bimodal'].sum().reset_index() # in %

        controls['sample density'] = controls['samples']/n_meanders
        max_sample_density = unknown['sample density'].max()

        sample_densities_trunc= [d for d in sample_densities_to_save if d <= max_sample_density]
        
        for d in sample_densities_trunc:
            unknown_d_bimodal = unknown_g[unknown_g['sample density']==d]['bimodal'].iloc[0]
            controls_d = controls[controls['sample density']==d]
            controls_d_bimodal = []
            for name in names_controls:
                num_bimodal = controls_d[controls_d['name']==name]['bimodal'].sum()
                controls_d_bimodal.append(num_bimodal)

            kde = gaussian_kde(controls_d_bimodal, bw_method='scott')
            xs = np.linspace(0,100,num=1000)
            
            p_value_kde = (1 - kde.integrate_box_1d(-np.inf, unknown_d_bimodal))
            p_values.append([d, num_bimodal, unknown_d_bimodal, p_value_kde])

        df = pd.DataFrame(p_values, columns=['sample density', 'average bimodality rate controls',
                                             'bimodality rate unknown', 'p-value'])
        df.to_csv(os.path.join(dir_path, file_stem+f"_p_values.csv"))
  
