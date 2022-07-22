"""
This file has the default tluspy configurations soft-coded into it so that they can be easily changed at runtime. If you make changes to the default settings please copy this file and give it a name such as 'config_OLD.py' so that you may change back to the default settings at any time. The rest of this package looks for configurations only in tluspy.config
"""

#paths of executables within pkg
tlpath = 'bin/tlusty208'
synpath = 'bin/synspec54'

#Location of H I atomic data
h1_data = 'h1s16.dat'
#h1_data = 'h1.dat'

#for writting aux files
aux_no_convec = {
    'tAUDIV': 1,
    'iACC': 7,
    'nITER':60,
    'IHYDPR':2,
    }
aux_convec = {
    'IFRYB':1,
    'IPRINT':3,
    'ITEK':40,
    'IACC':40,
    'TAUDIV': 1e-2,
    'IDLST':0,
    'MLTYPE':2,
    'NDCGAP':5,
    'ICONRE':0,
    'IDEEPC':3,
    'CRFLIM':-10,
    'IMUCON':40,
    'ICONRS':5
    }

tl_version = 208
syn_version = 54

user = 'Ted Johnson, UCLA, tedjohnson12@g.ucla.edu'
