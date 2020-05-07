# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 15:41:17 2020

@author: Ahnaf Lodhi
"""

import os
import os
import matplotlib.pyplot as plt
from oct_converter.readers import E2E

def converter(path, dest):

    print("Starting Conversion")
    #List all the E2E files
    filenames = [name for name in os.listdir(path) if '.E2E' in name]
    try:
        # Create file path for E2E converter to read the file paths
        files_path = [path  + '/' + file for file in filenames]
        # files_path = [os.path.join(path, file) for file in filenames]
        for file in files_path:
            file = E2E(file)
            oct_volumes = file.read_oct_volume()
            for volume in oct_volumes:
                # print('{}.jpeg'.format(dest + '/' + volume.patient_id))
                volume.save('{}.jpeg'.format(dest + '/' + volume.patient_id))
                # print(volume.patient_id)
        return files_path
    except:
        print('There are no E2E files in the selected folder')
    

