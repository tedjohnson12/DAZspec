"""
This module is meant to quickly create the standard files needed to run tlusty 205
and synspec 51. This file will need to be updated as new versions come out.
"""
import pkgutil
import warnings
from . import config
from shutil import copyfile
from numpy import log10
from numpy import exp
from os import system

from datetime import datetime

class Parameters:
    """
    Structure to hold the data to create a model.
    """
    def __init__(self,name,teff,log_g,abns):
        """
        abns must be a dict of ints in number space.
        """
        self.name = name
        self.teff = int(teff)
        self.log_g = float(log_g)
        self.abns = abns
        #check if self.abns is correct
        warn = False
        temp_dict = {} # in case we have to correct something
        for elem in self.abns:
            if type(elem) != type(1):
                warn = True
            temp_dict[int(elem)] = self.abns[elem]
            if float(self.abns[elem]) < 0:
                warn = True
                temp_dict[int(elem)] = 10**self.abns[elem]
        if warn:
            warnings.warn('abns must be a dictionary where the keys are integer atomic numbers and the values are abundances in number space. Please do not use log[abn], though __init__ function tries to fix it.')
        self.abns = temp_dict
    
    def set_abn(self,atm_no,value):
        self.abns[atm_no] = value
    
    def __str__(self):
        s = '%s\tTeff = %i\tLog g = %.3f\n'%(self.name, self.teff,self.log_g)
        s = s + 'atm\tabn\n'
        for elem in self.abns:
            s = s + '%i\t%.3e\n'%(elem,self.abns[elem])
        return s

def calc_ML(teff, log_g):
    """
    Calculate the mixing length of a convective WD model given the Teff and the Log g using the formula given in Tremblay 2015. The constants are determined from a fitting.
    
    teff: effective temperature / [K]
    log_g: log10(g/[cm/s2])
    """
    g0 = log_g - 8
    T0 = (teff - 12000) / 1000 - 1.6 * g0
    #from a fitting
    a1 = 1.1989803e+0
    a2 = -1.8659403e+0
    a3 = 1.4425600e+0
    a4 = 6.4742170e-2
    a5 = -2.9996192e-2
    a6 = 6.0750771e-2
    a7 = -5.2572772e-2
    a8 = 5.4690218e+0
    a9 = -1.6330177e-1
    a10 = 2.8348941e-1
    a11 = 1.7353691e1
    a12 = 4.3545950e-1
    a13 = -2.1739157e-1
    ML = (a1 + (a2 + exp(a4*T0 +a5*g0)) * exp((a6 + a7*exp(a8*T0))*T0 + a9*g0)) + a10 * exp(-1*a11*((T0 - a12)**2 + (g0 - a13)**2))
    return ML


def get_file(filename):
    """
    return the contents of a file in the tluspy.files directory
    """
    data = pkgutil.get_data(__name__, filename)
    return data
    
def get_path(filename):
    """
    Get the full path of a file that sits in the tluspy directory.
    Example:
    >>> get_path('data/h1_da.dat')
    '/anaconda3/.../tluspy/data/h1_da.dat'
    
    filename: str
    """
    
    import tluspy
    s = tluspy.__file__
    to_pkg = s[:s.find('tluspy.py')]
    path = to_pkg + filename
    return path

def write_fort5(teff,log_g, aux, **kwargs):
    """
    Write a fort.5 file to the current directory given certain paramters.
    
    teff: effective temperature / [K]
    log_g: log10(g/[cm/s2])
    aux: str, the name of the file containing auxillary parameters.
    
    kwargs:
    lte = True: bool, whether or not the model is in local thermodynamic equilibrium.
    ltgray = True: bool, if True, model is calculated from scratch. Otherwise a starting model is required in the directory with the name fort.8
    frequencies = 1000: int, number of frequency points used in the 1D atmosphere model.
    nlevels = 9: int, number of H I energy levels to consider in the model.
    """
    
    #parse kwargs
    
    lte = kwargs.get('lte',True)
    ltgray = kwargs.get('ltgray',True)
    frequencies = kwargs.get('frequencies',1000)
    nlevels = kwargs.get('nlevels',9)
    
    #get data path
    path = get_path('data/%s' % config.h1_data)
    
    
    with open('fort.5','w') as file:
        file.write('%i  %.3f\n' % (teff, log_g))#20546  7.910
        file.write('%s  %s\n' % (str(lte)[0],str(ltgray)[0]))#T  T
        file.write('\'%s\'\n' % aux)
        file.write('%i\n' % frequencies)
        file.write('1\n')
        file.write('2 0 0\n')
        file.write('1     0     %i      0    0      0    \' H 1\' \'%s\'\n' % (nlevels,path))
        file.write('1     1     1      1      0      0    \' H 2\' \' \'\n')
        file.write('0     0     0      -1    0      0    \' \' \' \'')
    print('Finished writing fort.5')
    

def write_fort56(abns,**kwargs):
    """
    Write a fort.56 file to the current directory.
    
    abns: dict {atomic number: N/H} number space!
    
    kwargs:
    n_elems = 30: int number of elements to be considered
    abn0 = 1e-50: default abundance
    """
    
    #parse kwargs
    n_elems = kwargs.get('n_elems',30)
    abn0 = kwargs.get('abn0', 1e-50)
    
    
    #make sure abns in number space
    for elem in abns:
        if abns[elem] < 0:
            raise ValueError('The dictionary of abundances must be in number space. No log(N/H) please!')
    
    
    with open('fort.56','w') as file:
        file.write('%i\n' % n_elems)
        if 1 in abns:
            file.write('%i\t%.3e' %(1,abns[1]))
        else:
            file.write('%i\t%i\n' % (1,1))
        for i in range(2,n_elems+1):
            if i in abns:
                file.write('%i\t%.3e' %(i,abns[i]))
            else:
                file.write('%i\t%.1e' %(i,abn0))
            if i < n_elems:
                file.write('\n')
    print('Finished writing fort.56')
            

def write_fort55(w1,w2,**kwargs):
    """
    Write a fort.55 file to the current directory. There are a lot of settings that can be changed in this file.
    w1: int, the starting wavelength in angstroms
    w2: int, the ending wavelength in angstroms -- if <0 then wavelengths are all in vacuum
    w1 and w2 tell sysnspec over which wavelengths to create the synthetic spectrum.
    
    kwargs: the following descriptions are from the Hubeny and Lanz 2017 paper 1 pg 19-20:
    
    
    imode - sets the basic mode of operation:
        = 0 - normal synthetic spectrum;
        = 1 - spectrum for a few lines (obsolete);
        = 2 - continuum (plus H and He II lines) only;
        = 10 - spectrum with molecular lines.
        = -1 an "iron curtain option". In this case one only computes the opacity at the standard depth idstd (see below), but does not solve the transfer equation. It is usually used with an artificial input model atmosphere consisting of one single depth point.
        
    idstd - index of the "standard depth", which is defined as a depth where T = (2/3)Teff. Approximately, idstd = (2/3)ND, with ND being the total number of depth points of the model. This parameter is not critical; it only influences the selection of lines to be considered, set through the rejection parameter relop - see Appendix C
    
    iprin - when > 0 increases the amount of printed information in the standard output (essentially obsolete)
    
    inmod - an indicator of the input model:
        = 0 - the input model is a Kurucz model;
        = 1 - the input is a tlusty model;
        = 2 - the input model is an accretion disk model
    
    intrpl, ichang - set the change of the input model (rarely used);
    
    ichemc - if non-zero, indicates a change of abundances with respect to the input model. In this     case, file fort.56 is required;
    
    iophli - treatment of far Lalpha wings (obsolete); should be set to 0;
    
    nunalp, nunbet, nungam, nunbal - if any of them set to a non-zero value, the quasi-molecular satellites of Lalpha, Lbeta, Lgamma, and Halpha, respectively, are considered. In that case, additional input files containing the corresponding data are needed. These have to have the following names: laquasi.dat, lbquasi.dat, lgquasi.dat, and lhquasi.dat, respectively. They are distributed along with synspec.
    
    ifreq - the choice of the radiative transfer equation solver; namely if ifreq >= 10 one uses the Feautrier scheme, otherwise the DFE scheme - see Paper II. This option is rarely used; one usually uses the default value ifreq = 1.
    
    inlte - an auxiliary NLTE switch:
        = 0 - enforces LTE: lines are treated in LTE even if the input model is NLTE.
        > 0 - its actual value (1 or 2) sets the mode of evaluation of the populations of levels close to the ionization limit - see section 5.6;
    
    icontl, inlist - obsolete parameters, typically set to 0;
    
    ifhe2 - if set to a non-zero value, He II is treated as a hydrogenic ion (see Appendix A);
    
    ihydpr, ihe1pr, ihe2pr - if set to a non-zero value, these parameters invoke a special evaluation of line profiles of the respective atom/ion. In this case, additional input files with corresponding data are needed - see Appendix A;
    
    cutof0 - cutoff parameter: the opacity of any line except H and He II is cut at cutof0 A from its center;
    
    cutofs - dummy variable;
    
    relop - line rejection parameter: a line is rejected if the ratio of its line-center opacity to the continuum opacity at standard depth idstd is less than relop;
    
    space - spacing parameter, which represents the maximum distance of two neighboring wavelength points at the midpoint of the considered wavelength interval, that is, delta lambda <= space. The actual maximum spacing is proportional to the wavelength, delta lambda <= space * (alam0 + alam1)/(2lambda). For more details, see Appendix C.
    """
    
    #parse kwargs
    
    imode = kwargs.get('imode',0)#1
    idstd = kwargs.get('idstd',50)
    iprin = kwargs.get('iprin',3)
    inmod = kwargs.get('inmod',1)#2
    intrpl = kwargs.get('intrpl',0)
    ichang = kwargs.get('ichang',0)
    ichemc = kwargs.get('ichemc',1)
    iophli = kwargs.get('iophli',0)#3
    nunalp = kwargs.get('nunalp',1)
    nunbet = kwargs.get('nunbet',1)
    nungam = kwargs.get('nungam',1)
    nunbal = kwargs.get('nunbal',0)
    ifreq = kwargs.get('ifreq',1)#4
    inlte = kwargs.get('inlte',0)
    icontl = kwargs.get('icontl',0)
    inlist = kwargs.get('inlist',0)
    ifhe2 = kwargs.get('ifhe2',0)
    ihydpr = kwargs.get('ihydpr',2)#5
    ihe1pr = kwargs.get('ihe1pr',0)
    ihe2pr = kwargs.get('ihe2pr',0)
    cutof0 = kwargs.get('cutof0',3)#6
    cutofs = kwargs.get('cutofs',0)
    relop = kwargs.get('relop',0.0001)
    space = kwargs.get('space',0.01)
    
    
    
    
    #write file
    with open('fort.55', 'w') as file:
        file.write('%i\t%i\t%i\n'%(imode,idstd,iprin))
        file.write('%i\t%i\t%i\t%i\n'%(inmod,intrpl,ichang,ichemc))
        file.write('%i\t%i\t%i\t%i\t%i\n'%(iophli,nunalp,nunbet,nungam,nunbal))
        file.write('%i\t%i\t%i\t%i\t%i\n'%(ifreq,inlte,icontl,inlist,ifhe2))
        file.write('%i\t%i\t%i\n'%(ihydpr,ihe1pr,ihe2pr))
        file.write('%i\t%i\t%f\t%i\t%f\t%f\n'%(w1,w2,cutof0,cutofs,relop,space))
    print('Finshed writing fort.55')


def write_aux(filename,teff,log_g):
    """
    Write an aux file given a filename, teff, and log_g.
    There are two modes that depend on the teff. For warmer models there is no convection considered.
    
    filename: str, name of the aux file
    teff: Teff/[K]
    log_g: log(g/[cm/s2])
    """
    if teff > 15000:
        with open(filename,'w') as file:
            for param in config.aux_no_convec:
                if type(config.aux_no_convec[param]) == int:
                    file.write('%s=%i\n' % (param,config.aux_no_convec[param]))
                else:
                    file.write('%s=%.3e\n' % (param,config.aux_no_convec[param]))
    
    else:
        ML = calc_ML(teff, log_g)
        with open(filename, 'w') as file:
            file.write('HMIX0=%.3f\n' % ML)
            for param in config.aux_convec:
                if type(config.aux_convec[param]) == int:
                    file.write('%s=%i\n' % (param,config.aux_convec[param]))
                else:
                    file.write('%s=%.3e\n' % (param,config.aux_convec[param]))
    print('Finished writing %s' % filename)



def read_abn_file(filename, **kwargs):
    """
    Read a file containing abundnace information. This is a file format that Beth uses to send information for models to Detlev, for example:
    
    ...HEADER...
    .
    .
    .
    el  at_no   log(N/H)
    C   6       -6.830
    ...
    
    returns a dictionary {6:1.48e-7, ...}
    
    there is one switch to tell the program that the file abundances are in number space
    
    kwargs:
    log=True: bool, is the file in log(N/H)
    """
    log = kwargs.get('log',True)
    
    
    els = []
    atm_nos = []
    abns = []
    abn_dict = {}
    with open(filename,'r') as file:
        for line in file:
            data = line.split('\t')
            if len(data)==3:
                if 'el' in line:
                    pass
                else:
                    els.append(data[0])
                    atm_nos.append(int(data[1]))
                    abns.append(float(data[2]))
    # turn into dictionary
    for i in range(1,30):
        if i in atm_nos:
            j = atm_nos.index(i)
            if log:
                abn_dict[i] = 10**abns[j]
            else:
                abn_dict[i] = abns[j]
        else:
            abn_dict[i] = 1e-50
    abn_dict[1] = 1
    return abn_dict

def get_linelist(filename):
    """
    Get a linelist from tluspy/linelists/filename
    You can even make your own so long as you follow the file convention.
    """
    path = get_path('linelists/%s' % filename)
    copyfile(path,'fort.19')
    print('Got linelist')
    




def add_header(filename, params, **kwargs):
    """
    Copy the data from fort.7 to a new file filename but put a header first so that you can run do_spec.do_model_linear_all()
    
    filename: str
    params: Parameters object
    
    kwargs:
    dt_suffix=False: bool append _yyymmdd-hhmm to end of filename
    """
    
    dt_suffix = kwargs.get('dt_suffix',False)
    now = datetime.now()
    dt_s = now.strftime('%Y%m%d-%H%M%S')
    
    if dt_suffix:
        filename = filename +'_' + dt_s
    
    
    #get convection string
    conv_str = 'Convection: None'
    
    if params.teff <= 15000:
        ML = calc_ML(params.teff,params.log_g)
        conv_str = 'Convection: ML2 = %.2f' % ML
    
    
    with open(filename + '.tl', 'w') as file:
        file.write('TEFF     = %i\n' % params.teff)
        file.write('LOG_G    = %.2f\n' % params.log_g)
        file.write('COMMENT    Tlusty version %i\n' % config.tl_version)
        file.write('COMMENT    Synspec version %i\n' % config.syn_version)
        file.write('COMMENT    Generated %s\n' % dt_s)
        file.write('COMMENT    User: %s\n' % config.user)
        file.write('COMMENT    Star Name %s\n' % params.name)
        file.write('COMMENT    %s\n' % conv_str)
        file.write(    'COMMENT    el  log[N/H]  [N/H]\n')
        for elem in params.abns:
            file.write('COMMENT    %02d   %.2f     %.2e\n' % (elem,log10(params.abns[elem]), params.abns[elem]))
        #now just default stuff to convert to fits
        file.write('NAXIS    = 2\n')
        file.write('TTYPE1   = \'wavelength\'\n')
        file.write('TUNIT1   = \'Angstrom\'\n')
        file.write('TTYPE2   = \'Flambda\'\n')
        file.write('TUNIT2   = \'erg/cm2/s/Angstrom\'\n')
        file.write('COMMENT    Air wavelengths > 200 nm\n')
        file.write('END\n')
        with open('fort.7', 'r') as infile:
            for line in infile:
                file.write(line)
        print('Header Added to file %s' % filename + '.tl')
        return(filename + '.tl')
        
    
def move():
    """
    rename fort.7 to fort.8
    """
    system('mv fort.7 fort.8')
