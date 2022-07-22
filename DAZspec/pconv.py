import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import colorama
from colorama import Fore
from colorama import Style

colorama.init()


#load filedata

def load_fort7():
    """
    Parse the fort.7 file in the pwd and get an array of the depth points. This is the first block in the fort.7 file. Editing this code can allow one to get out the second block, named b2.
    """
    b1 = []
    b2 = []
    i = 0
    temp = []
    with open('fort.7','r') as file:
        file.readline()
        for line in file:
            line = line.replace('D','e')
            if line[1].isspace(): #block 2
                i += 1
                temp += line.split()
                if i == 3:
                    b2.append(temp)
                    temp = []
                    i = 0
            else: # block 1
                b1 += line.split()
                i=0
    mass = np.flip(np.array(b1,dtype='float32'))
    return mass


def load_fort9():
    """
    Parse the fort.9 file in the pwd and return the data stored as a Pandas DataFrame.
    """
    df = pd.read_csv('fort.9',skiprows=1,delimiter='[ ]+',engine='python')
    df = df.replace('D','e', regex=True)
    for col in df.columns:
        df[col] = np.array(df[col],dtype = 'float32')
    return df

def load_fort69():
    """
    Parse fort.69 from pwd to get timing info.
    return the time in s as a float.
    """
    
    t = 0
    with open('fort.69', 'r') as file:
        for line in file:
            t = float(line.split()[2])
    return t


def load_fort6():
    """
    Parse the fort.6 file from pwd to check the conservation of flux. This should not be more than 1%.
    returns the fractional deviation as a percentage
    
    Updated to work for tlusty208
    """
    
    s=''
    with open('fort.6', 'r') as file:
        s = file.read()
    s = s[s.find('FINAL MODEL ATMOSPHERE'):]
    
    cols = s[s.find('ID'):].split('\n')[0].split()
    table = s[s.find('(RAD+CON)/TOT')+len('(RAD+CON)/TOT\n\n'):].replace('D','e')
    df = pd.DataFrame([x.split() for x in table.split('\n')[:-1]], columns=cols)
    flux = np.array(df['(RAD+CON)/TOT'],dtype='float32')
    return abs(flux-flux.mean()).max()/flux.mean() * 100



#now make plots

def pconv(**kwargs):
    """
    Plot the convergence log and return a figure that can be used to check for convergence.
    kwargs:
    s is a string that should contain some kind of description if many runs are being done at once.
    figsize is a tuple (w,h) in inches
    """
    s = kwargs.get('s','')
    figsize = kwargs.get('figsize',(14,10))
    
    #scale font with fig size
    fontsize = int(18 / 14 * figsize[0])
    
    fig,ax = plt.subplots(2,3, figsize = figsize)
    ax = np.ravel(ax)
    df = load_fort9()
    mass = load_fort7()
    colors = plt.cm.viridis(np.linspace(0,1,len(set(df['ITER'])))) # the colors for the plot
    
    font = {'size':fontsize,
            'family':'serif'
                }
    for i in set(df['ITER']):
        idata = df['ITER'] == i
        ax[0].plot(np.log(mass),df[idata]['TEMP'],c=colors[int(i-1)])
        ax[0].axhline(0,c='k',linestyle='--',lw=1)
        ax[1].plot(np.log(mass),np.log10(abs(df[idata]['TEMP'])),c=colors[int(i-1)])
        ax[1].axhline(0,c='k',linestyle='--',lw=1)
        ax[3].plot(np.log(mass),df[idata]['MAXIMUM'],c=colors[int(i-1)])
        ax[3].axhline(0,c='k',linestyle='--',lw=1)
        ax[4].plot(np.log(mass),np.log10(abs(df[idata]['MAXIMUM'])),c=colors[int(i-1)])
        ax[4].axhline(0,c='k',linestyle='--',lw=1)
    
    ax[2].plot(np.array(list(set(df['ITER']))),np.array(df.groupby('ITER').apply(max)['TEMP']),'-Xk')
    ax[5].plot(np.array(list(set(df['ITER']))),np.array(df.groupby('ITER').apply(max)['MAXIMUM']),'-Xk')
    #labels
    ax[0].set_ylabel('Relative Change')
    ax[0].set_xlabel('Log Depth (Mass)')
    ax[0].set_title('Temperature')
    
    ax[1].set_xlabel('Log Depth (Mass)')
    ax[1].set_title('Temperature')
    
    ax[2].set_xlabel('Iteration')
    ax[2].set_title('Temperature')
    
    ax[3].set_ylabel('Relative Change')
    ax[3].set_xlabel('Log Depth (Mass)')
    ax[3].set_title('Maximum in State Vector')
    
    ax[4].set_xlabel('Log Depth (Mass)')
    ax[4].set_title('Maximum in State Vector')
    
    
    ax[5].set_xlabel('Iteration')
    ax[5].set_title('Maximum in State Vector')
    
    #time and flux
    
    fig.subplots_adjust(right=0.7)
    
    t = load_fort69()
    f = load_fort6()
    if f>=1.0:
        print(Fore.RED + 'Warning: Departure from flux equillibrium of %.1f pct. May be Result of poor convergence.' + Style.RESET_ALL)
    fig.text(0.71,0.85,'Time=%.2f s' % t, fontdict=font)
    fig.text(0.71,0.75,'Max Departure\nfrom Flux Unity\n=%0.2f pct' % f, fontdict=font)
    fig.suptitle(s, fontdict=font)
    
    return fig
    
    
