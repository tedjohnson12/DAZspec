#written by Ted Johnson. I would like to make operation of Tlusty and Synspec nicer. This library should aid in automation, but by itself is probably not super easy to use.
#DISCLAIMER - this should only be used for White Dwarfs. For full versitility use the real code.
#This is built to interact with Tlusty and Synspec, but is nothing more than a shell around them.

import os
import numpy as np
from .files import get_path
import config

    


    



def tlusty():
    """
    Run tlusty with file name defined in tluspy.config.
    """
    path = get_path(config.tlpath)
    os.system('%s < fort.5 > fort.6' % path)
    
def synspec():
    """
    Run synspec with file name defined in tluspy.config.
    """
    path = get_path(config.synpath)
    os.system('%s < fort.5 > fort.6' % path)
