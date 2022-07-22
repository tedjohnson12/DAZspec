import os
from tluspy.files.files import get_path

original_cwd = os.getcwd()

tl_buildpath = get_path('bin/tluspy')
syn_buildpath = get_path('bin/synspec')

# compile tlusty
os.chdir(tl_buildpath)
os.system('gfortran -fno-automatic -03 -o ..tlusty.exe tlusty205.f')
