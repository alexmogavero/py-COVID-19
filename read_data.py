from os import path
import json
from matplotlib import pyplot, dates
from dateutil import parser
from datetime import timedelta
from scipy.optimize import curve_fit
from math import pow, log
import numpy as np

DATA_DIR = "/home/oslo/Software/COVID-19/dati-json/"
FILE_STATO = "dpc-covid19-ita-andamento-nazionale.json"
FILE_REG = "dpc-covid19-ita-regioni.json"

def plot_data(data_dict, shift=0, ax=None, name=''):
    t = [parser.parse(dt['data']) for dt in data_dict]
    y = [dt['totale_casi']-shift for dt in data_dict]
    
    t_fit = range(7)
    t_fit = t + [t[-2] + timedelta(days=tt) for tt in t_fit]
    fit_label, y_fit = fit_data(t,y,t_fit)[0:2]
    
    if ax is None:
        pyplot.figure()
        ax = pyplot.axes()
        ax.set_prop_cycle(color=['b','b','r','r','g','g','m','m','c','c','k','k'])
        pyplot.xlabel('Data')
        pyplot.ylabel('totale casi')
        formatter = dates.DateFormatter('%d/%m')
        ax.xaxis.set_major_formatter(formatter)
        
    ax.plot_date(t,y)
    ax.plot_date(t_fit,y_fit,fmt='-',label=name + ' ' + fit_label)
    ax.legend()
    
    return ax
    
    
def exp_fun(t,tau,i0):
    return i0*np.exp(t/tau)

def fit_data(t,y,*argv):
    t_float = np.array([(tt-t[0])/timedelta(days=1) for tt in t])
    y = np.array(y)
    t_float = t_float[y>0]
    y = y[y>0]
    popt, pcov = curve_fit(exp_fun, t_float, y)
    
    t0 = log(popt[1])*popt[0]
    label = 'tau={:.2f} t0={:.2f}'.format(popt[0],t0)
        
    if len(argv)>0:
        t_fit = argv[0]
        
        t_fit_float = np.array([(tt-t[0])/timedelta(days=1) for tt in t_fit])
        y_fit = exp_fun(t_fit_float, *popt)  
    
        return label, y_fit, popt
    else:
        return label, popt
    
def plot_regione(data_dict, reg):
    if not isinstance(reg, list):
        reg = [reg]
        
    ax = None
    for nome_reg in reg:
        if len(reg)>1:
            nm = nome_reg
        else:
            nm = ''
            
        if nome_reg=='Lazio':
            ax = plot_data([d for d in data_dict if d['denominazione_regione']==nome_reg],
                    shift=3, ax=ax, name=nm)
        else:
            ax = plot_data([d for d in data_dict if d['denominazione_regione']==nome_reg],
                    ax=ax, name=nm)
            
    pyplot.title(nome_reg)
    
def plot_stato(data_dict):
    plot_data(data_dict)
    pyplot.title('Italia')
    
def summary_regioni(data_dict):
    r_name = set([d['denominazione_regione'] for d in data_dict])
    
    for nm in r_name:
        if nm == 'Lazio':
            shift = 3
        else:
            shift = 0
            
        t = [parser.parse(dt['data']) for dt in data_dict if dt['denominazione_regione']==nm]
        y = [dt['totale_casi']-shift for dt in data_dict if dt['denominazione_regione']==nm]
        
        label = fit_data(t,y)[0]
        
        print('{}: {}'.format(nm, label))

if __name__=="__main__":
    with open(path.join(DATA_DIR,FILE_REG), 'r') as f:
        data_reg = json.load(f)
        
    with open(path.join(DATA_DIR,FILE_STATO), 'r') as f:
        data_stato = json.load(f)
        
    plot_regione(data_reg, ['Campania', 'Lazio'])
    
    plot_regione(data_reg, 'Calabria')
    
    plot_regione(data_reg, 'Lombardia')
    
    plot_stato(data_stato)
    
    summary_regioni(data_reg)
    
    pyplot.show()
