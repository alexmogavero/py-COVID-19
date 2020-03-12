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

def plot_data(data_dict, shift=0):
    t = [parser.parse(dt['data']) for dt in data_dict]
    y = [dt['totale_casi']-shift for dt in data_dict]
    
    t_fit = range(7)
    t_fit = t + [t[-2] + timedelta(days=tt) for tt in t_fit]
    fit_label, y_fit = fit_data(t,y,t_fit)
    
    pyplot.figure()
    ax = pyplot.axes()
    pyplot.plot_date(t,y)
    pyplot.plot_date(t_fit,y_fit,fmt='-',label=fit_label)
    formatter = dates.DateFormatter('%d/%m')
    ax.xaxis.set_major_formatter(formatter)
    ax.legend()
    pyplot.xlabel('Data')
    pyplot.ylabel('totale casi')
    
def exp_fun(t,tau,i0):
    return i0*np.exp(t/tau)

def fit_data(t,y,t_fit):
    t_float = np.array([(tt-t[0])/timedelta(days=1) for tt in t])
    y = np.array(y)
    t_float = t_float[y>0]
    y = y[y>0]
    popt, pcov = curve_fit(exp_fun, t_float, y)
    
    t_fit_float = np.array([(tt-t[0])/timedelta(days=1) for tt in t_fit])
    y_fit = exp_fun(t_fit_float, *popt)
    
    t0 = log(popt[1])*popt[0]
    label = 'tau={:.2f} t0={:.2f}'.format(popt[0],t0)
    return label, y_fit
    
def plot_regione(data_dict, nome_reg):
    if nome_reg=='Lazio':
        plot_data([d for d in data_dict if d['denominazione_regione']==nome_reg], shift=3)
    else:
        plot_data([d for d in data_dict if d['denominazione_regione']==nome_reg])
        
    pyplot.title(nome_reg)
    
def plot_stato(data_dict):
    plot_data(data_dict)
    pyplot.title('Italia')

if __name__=="__main__":
    with open(path.join(DATA_DIR,FILE_REG), 'r') as f:
        data_reg = json.load(f)
        
    with open(path.join(DATA_DIR,FILE_STATO), 'r') as f:
        data_stato = json.load(f)
        
    plot_regione(data_reg, 'Campania')
    
    plot_regione(data_reg, 'Lazio')
    
    plot_regione(data_reg, 'Lombardia')
    
    plot_stato(data_stato)
    
    pyplot.show()
