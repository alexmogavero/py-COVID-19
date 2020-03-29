#!/usr/bin/python3

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

def plot_data(data_dict, shift=0, ax=None, name='', y_name='totale_casi'):
    t = [parser.parse(dt['data']) for dt in data_dict]
    y = [dt[y_name]-shift for dt in data_dict]
    
    t_fit = range(7)
    t_fit = t + [t[-2] + timedelta(days=tt) for tt in t_fit]
    fit_label, y_fit = fit_data(t,y,t_fit)[0:2]
    
    if ax is None:
        pyplot.figure()
        ax = pyplot.axes()
        ax.set_prop_cycle(color=['b','b','r','r','g','g','m','m','c','c','k','k'])
        pyplot.xlabel('Data')
        pyplot.ylabel(y_name)
        formatter = dates.DateFormatter('%d/%m')
        ax.xaxis.set_major_formatter(formatter)
        
    ax.plot_date(t,y)
    ax.plot_date(t_fit,y_fit,fmt='-',label=name + ' ' + fit_label)
    ax.legend()
    
    return ax
     
class Fitting(object):
    def __init__(self, t, y):
        super().__init__()
        
        t = self._preprocess(t)
        t, y = self._removeData(t, y) 
        
        self._fit(t, y)
        
    def _fit(self,t,y):
        popt = curve_fit(self._func, t, y)[0]
        
        self.param = popt
        
    @staticmethod
    def _preprocess(t):
        t_float = np.array([(tt-t[0])/timedelta(days=1) for tt in t])
        
        return t_float
    
    @staticmethod
    def _removeData(t,y):
        y = np.array(y)
        t = t[y>0]
        y = y[y>0]
        
        return t, y
     
    @staticmethod   
    def _func(t,*argv):
        raise NotImplementedError('Method _func not implemented!')
    
    def label(self):
        raise NotImplementedError('Method label not implemented!')
    
    def evaluate(self, t):
        t = self._preprocess(t)
        return self._func(t, *self.param)
        
class Exponential(Fitting):
    def __init__(self, t, y):
        super().__init__(t, y)
        
    @staticmethod
    def _func(t,tau,i0):
        return i0*np.exp(t/tau)
    
    def label(self):
        tau = self.param[0]
        i0 = self.param[1]
        t0 = log(i0)*tau
        return 'tau={:.2f} t0={:.2f}'.format(tau,t0)
        
class Logistica(Fitting):
    def __init__(self, t, y):
        super().__init__(t, y)
        
    def _fit(self,t,y):
        popt = curve_fit(self._func, t, y, p0=[1000.0,100.0,0.2])[0]
        
        self.param = popt
        
    @staticmethod
    def _func(t,K,C,h):
        return K/(1 + C*np.exp(-h*t))
    
    def label(self):
        return 'K={:.2f} C={:.2f} h={:.2f}'.format(*self.param)

def fit_data(t,y,*argv):
    f = Logistica(t, y)
    
    label = f.label()
        
    if len(argv)>0:
        t_fit = argv[0]
        
        y_fit = f.evaluate(t_fit)  
    
        return label, y_fit
    else:
        return label
    
def plot_regione(data_dict, reg, y_name='totale_casi'):
    if not isinstance(reg, list):
        reg = [reg]
        
    ax = None
    for nome_reg in reg:
        if len(reg)>1:
            nm = nome_reg
        else:
            nm = ''
            
        if nome_reg=='Lazio':
            shift = 3
        else:
            shift = 0
            
        ax = plot_data([d for d in data_dict if d['denominazione_regione']==nome_reg],
                    shift=shift, ax=ax, name=nm, y_name=y_name)
            
    pyplot.title(nome_reg)
    
def plot_stato(data_dict, y_name='totale_casi'):
    plot_data(data_dict, y_name=y_name)
    pyplot.title('Italia')
    
def summary_regioni(data_dict, y_name='totale_casi'):
    r_name = set([d['denominazione_regione'] for d in data_dict])
    
    for nm in r_name:
        if nm == 'Lazio':
            shift = 3
        else:
            shift = 0
            
        t = [parser.parse(dt['data']) for dt in data_dict if dt['denominazione_regione']==nm]
        y = [dt[y_name]-shift for dt in data_dict if dt['denominazione_regione']==nm]
        
        label = fit_data(t,y)
        
        print('{}: {}'.format(nm, label))

if __name__=="__main__":
    with open(path.join(DATA_DIR,FILE_REG), 'r') as f:
        data_reg = json.load(f)
        
    with open(path.join(DATA_DIR,FILE_STATO), 'r') as f:
        data_stato = json.load(f)
        
    y_name = 'totale_ospedalizzati'
        
    plot_regione(data_reg, ['Lazio', 'Campania'], y_name=y_name)
    
    plot_regione(data_reg, 'Campania', y_name=y_name)
    
    plot_regione(data_reg, 'Lombardia', y_name=y_name)
    
    plot_stato(data_stato, y_name=y_name)
    
    summary_regioni(data_reg, y_name=y_name)
    
    pyplot.show()
