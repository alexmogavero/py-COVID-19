from os import path
import json
from matplotlib import pyplot, dates
from dateutil import parser
from datetime import timedelta
from scipy.optimize import curve_fit
from math import pow
import numpy as np

DATA_DIR = "/home/oslo/Software/COVID-19/dati-json/"
FILE_STATO = "dpc-covid19-ita-andamento-nazionale.json"
FILE_REG = "dpc-covid19-ita-regioni.json"

def plot_data(data_dict):
    t = [parser.parse(dt['data']) for dt in data_dict]
    y = [dt['totale_casi'] for dt in data_dict]
    
    popt, y_fit = fit_data(t,y)
    print(popt, y_fit)

    pyplot.figure()
    ax = pyplot.axes()
    pyplot.plot_date(t,y)
    formatter = dates.DateFormatter('%d/%m')
    ax.xaxis.set_major_formatter(formatter)
    pyplot.xlabel('Data')
    pyplot.ylabel('totale casi')
    
def exp_fun(t,a,b):
    return np.power(a,b*t)

def fit_data(t,y):
    t_float = [(tt-t[0])/timedelta(days=1) for tt in t]
    popt, pcov = curve_fit(exp_fun, t_float, y)
    y_fit = exp_fun(t_float, popt[0], popt[1])
    return popt, y_fit
    
def plot_regione(data_dict, nome_reg):
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
    
    plot_stato(data_stato)
    
    pyplot.show()
