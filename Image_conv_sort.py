# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 18:53:55 2020
E2E Conversion:
    Step 1: Select Destination directory
    Step 2: Select source directory. Conversion will start automatically with this step
    
Image Labelling:
    Step 1: Select the Label Directory. All the labeled images will be moved here within their respective subfolders
    Step 2: Select the Image directory (containing all the images). This has to be completed every time at the start of runtime.
@author: user
"""
# In[5]:
##### added in version 2

# the folder in which the pictures that are to be sorted are stored
# don't forget to end it with the sign '/' !
# input_folder = '/file_path/to/image_folder/'
# input_folder = '../OCT/image_set/OCT/'
# input_folder = './image_folder/'
input_folder = '../../MACTEL_E2E/OCT_V2/'


# the different folders into which you want to sort the images, e.g. ['cars', 'bikes', 'cats', 'horses', 'shoes']
# labels = ["MTP", "NORMAL"]
labels = ["MTP", "NORMAL", "DME", "DRUSEN", "CNV", "MTP-Probable", "Exclude"]

# provide either 'copy' or 'move', depending how you want to sort the images into the new folders
# - 'move' starts where you left off last time sorting, no 'go to #pic', works with number-buttons for labeling, no txt-file for tracking after closing GUI, saves memory
# - 'copy' starts always at beginning, has 'go to #pic', doesn't work with number-buttons, has a txt-for tracking the labels after closing the GUI
copy_or_move = 'move'

# Only relevant if copy_or_move = 'copy', else ignored
# A file-path to a txt-file, that WILL be created by the script. The results of the sorting wil be stored there.
# Don't provide a filepath to an empty file, provide to a non-existing one!
# If you provide a path to file that already exists, than this file will be used for keeping track of the storing.
# This means: 1st time you run this script and such a file doesn't exist the file will be created and populated,
# 2nd time you run the same script, and you use the same df_path, the script will use the file to continue the sorting.
# df_path = '/file_path/to/non_existing_file_df.txt'

df_path = './labels.txt'

# a selection of what file-types to be sorted, anything else will be excluded
file_extensions = ['.jpg', '.png', '.tiff', '.jpeg']
#####

import pandas as pd
import os
import tkinter as tk
import tkinter.filedialog
from shutil import copyfile, move
from PIL import ImageTk, Image
from converter import converter
import matplotlib.pyplot as  plt

class ImageGUI():
    
    e2e = 0
    im_select = 0
    label_flag = 0
    def __init__(self, root):
        root.title('E2E Data Conversion and Labelling')
        root.geometry('1000x950')
                
        frame = tk.Frame(root)
        frame.grid() 
        
        self.dest_dir = 'None'
        self.source_directory = 'None'
        self.img_dir = 'None'
        self.label_dir = 'None'
        
        self.paths = 'None'
        self.labels = labels
        
        self.n_paths = 'None'
        self.n_labels = 'None'
        
        self.index = 0
        
        # Set empty image container
       
        self.image_raw = None
        self.image = None
        self.image_panel = tk.Label(frame)
        
        # set image container to first image
        # self.set_image('C:/Users/user/Desktop/Labelling/image-sorter2-master/image_folder/1.jpg')

        # Make buttons
        self.Catbuttons = []
        for label in labels:
            self.Catbuttons.append(
                    tk.Button(frame, text=label, width=12, height=2, fg='blue', command=lambda l=label: self.vote(l))
            )
            
        ### added in version 2
        self.Loadbuttons = []
        
        self.Loadbuttons.append(tk.Button(frame, text="1a. Destination E2E-Jpg", width=18, height=1, fg='green', 
                                      command=lambda l=label: self.DestDialog()))
        
        self.Loadbuttons.append(tk.Button(frame, text="2a. E2E Directory", width=16, height=1, fg='green', 
                                      command=lambda l=label: self.FileDialog()))
                        
        self.Loadbuttons.append(tk.Button(frame, text="1b. Image Directory", width=16, height=1, fg='green', 
                                      command=lambda l=label: self.ImgDirDialog()))
        
        self.Loadbuttons.append(tk.Button(frame, text="2b. Label Directory", width=16, height=1, fg='green', 
                                      command=lambda l=label: self.make_folder()))

        self.Actbuttons = []
        self.Actbuttons.append(tk.Button(frame, text="Prev im", width=10, height=1, fg="green", 
                                      command=lambda l=label: self.move_prev_image()))
        
        self.Actbuttons.append(tk.Button(frame, text="Next im", width=10, height=1, fg='green', 
                                      command=lambda l=label: self.move_next_image()))
        
        ###
        # Place buttons in grid
        
        for ii, button in  enumerate(self.Loadbuttons):
            button.grid(row = 0, column = ii, sticky = 'we')
            
            
        for jj, button in  enumerate(self.Actbuttons):
            button.grid(row = 0, column = len(self.Loadbuttons)+jj+1, sticky = 'we')
            
        for kk, button in enumerate(self.Catbuttons):
            button.grid(row=1, column= kk, sticky='we')
            
            
        #frame.grid_columnconfigure(ll, weight=1)
        
         #### Added in version 2
        
        # Add sorting label
        #sorting_string = df.sorted_in_folder[self.index].split(os.sep)[-2]
        sorting_string = 'None'
        # sorting_string = df.sorted_in_folder[self.index].split("/")[-2]
        self.sorting_label = tk.Label(frame, text=("In folder: %s" % (sorting_string)), width=15)
        
         # Place sorting label in grid
        self.sorting_label.grid(row=3, column=4, columnspan = 2,  sticky='we') # +2, since progress_label is placed after
                                                                            # and the additional 2 buttons "next im", "prev im"
                
        # Add progress label
        
        progress_string = "Images: %d/%d" % (0, 0)
        self.progress_label = tk.Label(frame, text=progress_string, width=10)
        
        # Place progress label in grid
        self.progress_label.grid(row=2, column=4, sticky='we') # +2, since progress_label is placed after
                                                                            # and the additional 2 buttons "next im", "prev im"
        
        # Add File Name
        display_name = "Name = %s" % ('None')
        self.name_label = tk.Label(frame, text = display_name, width =10)
        
        # Place name label in grid
        self.name_label.grid(row=2, column=1, columnspan =3,  sticky='we') # +2, since progress_label is placed after
                                                                            # and the additional 2 buttons "next im", "prev im"
        # Add Current Label
        cat_name = 'Current Category : %s' %('None')
        self.cat_label = tk.Label(frame, text = cat_name, width  = 10)
        
        # Place Category label in the grid
        self.cat_label.grid(row = 2, column = 0, columnspan = 1, sticky = 'we')
        
        status = 'None'
        self.convert_status =tk.Label(frame, text = ('Coverter Status = %s ' %(status)), width = 20)
        self.convert_status.grid(row = 4, column = 4, columnspan = 2)
        
            
        instr_head = 'Intructions'
        instructions = """
        2 Step Process: E2E Conversion and Image Labelling
        
        1. E2E Conversion: Step wise 
        1a. Select Destination E2E-Jpg . 
        This is the location where the image slices from the conversion will be stored.
        
        2a. E2E Directory: Select E2E Directory where the E2E data is stored.
        Once selected, the conversion of the data placed in this folder will start automatically.
        
        
        2. Labelling: 
        1b. Select Image Directory first.
        This is the location containing the slice images.
        2b. Select Label Directory .
        This is the location where the images will be moved upon labelling.
        All the images will be placed in their label sub-folders'.
        The information will be updated once you click on Next Image.
        
        Important:
        Do not proceed with Labelling while Conversion is being carried out. 
        """
        self.instruction_head = tk.Label(frame, text = instr_head, width  = 10)
        self.instruction_head.grid(row = 5, column = 5, sticky = 'we')
        
        self.instructions = tk.Label(frame, text = instructions, width = 20, justify = 'left', 
                                     wraplength = 400, padx = 3)
        self.instructions.grid(row = 6, rowspan = 7, column = 3, columnspan =6, sticky = 'we')
        
        # Place the image in grid
        self.image_panel.grid(row=3, column=0, rowspan = 10,  columnspan = 3, sticky='we')
        
        
        # Place typing input in grid, in case the mode is 'copy'
        if copy_or_move == 'copy':
            tk.Label(frame, text="go to #pic:").grid(row=1, column=0)

            self.return_ = tk.IntVar() # return_-> self.index
            self.return_entry = tk.Entry(frame, width=6, textvariable=self.return_)
            self.return_entry.grid(row=1, column=1, sticky='we')
            root.bind('<Return>', self.num_pic_type)
        ####   
    
    def show_next_image(self):
        """
        Displays the next image in the paths list and updates the progress display
        """
        self.index += 1
        progress_string = "%d/%d" % (self.index+1, self.n_paths)
        self.progress_label.configure(text=progress_string)
        
        display_name = "Name = %s" % (self.file_names[self.index])
        self.name_label.configure(text = display_name)
        
        #### added in version 2
        #sorting_string = df.sorted_in_folder[self.index].split(os.sep)[-2] #shows the last folder in the filepath before the file
        sorting_string = self.df.sorted_in_folder[self.index].split("/")[-2]
        self.sorting_label.configure(text=("In folder: %s" % (sorting_string)))
        
        #Add Current Label
        print(sorting_string)
        for label in labels:
            if label not in sorting_string:
                cat_string = 'Unlabelled'
            else:
                cat_string = sorting_string
            
        self.cat_label.configure(text = ('Current Category : %s' %(cat_string)))
        
        ####

        if self.index < self.n_paths:
            self.set_image(self.df.sorted_in_folder[self.index])
        else:
            self.master.quit()
    
    ### added in version 2
    def move_next_image(self):
        """
        Displays the next image in the paths list AFTER BUTTON CLICK,
        doesn't update the progress display
        """
        self.index += 1
        progress_string = "%d/%d" % (self.index+1, self.n_paths)
        self.progress_label.configure(text=progress_string)
        
        #sorting_string = df.sorted_in_folder[self.index].split(os.sep)[-2] #shows the last folder in the filepath before the file
        sorting_string = self.df.sorted_in_folder[self.index].split("/")[-2]
        self.sorting_label.configure(text=("In folder: %s" % (sorting_string)))
        
        # if 'OCT_V2' in sorting_string:
        #     cat_string = 'Unlabelled'
        # else:
        #     cat_string = 
        
        for label in labels:
            if label not in sorting_string:
                cat_string = 'Unlabelled'
            else:
                cat_string = sorting_string
            
        self.cat_label.configure(text = ('Current Category : %s' %(cat_string)))
        
        display_name = "Name = %s" % (self.file_names[self.index])
        self.name_label.configure(text = display_name)
        
        if self.index < self.n_paths:
            self.set_image(self.df.sorted_in_folder[self.index])
        else:
            self.master.quit()
            
     ### added in version 2        
    def move_prev_image(self):
        """
        Displays the prev image in the paths list AFTER BUTTON CLICK,
        doesn't update the progress display
        """
        self.index -= 1
        progress_string = "%d/%d" % (self.index+1, self.n_paths)
        self.progress_label.configure(text=progress_string)
        
        #sorting_string = df.sorted_in_folder[self.index].split(os.sep)[-2] #shows the last folder in the filepath before the file
        sorting_string = self.df.sorted_in_folder[self.index].split("/")[-2]
        self.sorting_label.configure(text=("In folder: %s" % (sorting_string)))

        #Add Current Label
        if 'OCT_V2' in sorting_string:
            cat_string = 'Unlabelled'
        else:
            cat_string = sorting_string
            
        self.cat_label.configure(text = ('Current Category : %s' %(cat_string)))
        
        display_name = "Name = %s" % (self.file_names[self.index])
        self.name_label.configure(text = display_name)
        
        if self.index < self.n_paths:
            self.set_image(self.df.sorted_in_folder[self.index]) # change path to be out of df
        else:
            self.master.quit()
            
    def vote(self, label):
        """
        Processes a vote for a label: Initiates the file copying and shows the next image
        :param label: The label that the user voted for
        """
        ##### added in version 2
        # check if image has already been sorted (sorted_in_folder != 0)
        if self.df.sorted_in_folder[self.index] != self.df.im_path[self.index]:
            # if yes, use as input_path the current location of the image
            input_path = self.df.sorted_in_folder[self.index]
            root_ext, file_name = os.path.split(input_path)
            root, _ = os.path.split(root_ext)
        else:
            # if image hasn't been sorted use initial location of image
            input_path = self.df.im_path[self.index]
            root, file_name = os.path.split(input_path)
            
        #####
        
        #input_path = self.paths[self.index]
        if copy_or_move == 'copy':
            self._copy_image(self, label, self.index)
        if copy_or_move == 'move':
            self._move_image(self, label, self.index)
        
        self.show_next_image()
        
    def vote_key(self, event):
        """
        Processes voting via the number key bindings.
        :param event: The event contains information about which key was pressed
        """
        pressed_key = int(event.char)
        label = self.labels[pressed_key-1]
        self.vote(label)
        
    def ImgDirDialog(self):
        """
        Image Folder has to be selected everytime for requisite information to be updated.
        All the information is being updated here.
        
        """
        
        self.img_dir = tk.filedialog.askdirectory(title = "Select Destination Directory for image data")
        self.file_names = [fn for fn in sorted(os.listdir(self.img_dir)) if any(fn.endswith(ext) for ext in file_extensions)]
        self.paths = [self.img_dir + '/' + file_name for file_name in self.file_names]
        
        # Number of labels and paths
        self.n_labels = len(self.labels)
        self.n_paths = len(self.paths)
               
        # set image container to first image
        self.set_image(self.paths[self.index])
        
        # if copy_or_move == 'copy':
        #     try:
        #         df = pd.read_csv(df_path, header=0)
        #         # Store configuration file values
        #     except FileNotFoundError:
        #         df = pd.DataFrame(columns=["im_path", 'sorted_in_folder'])
        #         df.im_path = self.paths
        #         df.sorted_in_folder = self.paths
            
        if copy_or_move == 'move':
            self.df = pd.DataFrame(columns=["im_path", 'sorted_in_folder'])
            self.df.im_path = self.paths
            self.df.sorted_in_folder = self.paths
        
            
    def set_image(self, path):
        """
        Helper function which sets a new image in the image view
        :param path: path to that image
        """
        
        image = self._load_image(path)
        self.image_raw = image
        self.image = ImageTk.PhotoImage(image)
        self.image_panel.configure(image=self.image)
        
        
    @staticmethod
#     def _load_image(path, size=(400,700)):
    def _load_image(path):  
        """
        Loads and resizes an image from a given path using the Pillow library
        :param path: Path to image
        :param size: Size of display image
        :return: Resized image
        """
        image = Image.open(path)
        size = image.size
                
        image = image.resize((550,550), Image.ANTIALIAS)
#         image = image.thumbnail((200,200), Image.ANTIALIAS)
        return image
    
    @staticmethod
    def _move_image(self, label, ind):
        """
        Moves a file to a new label folder using the shutil library. The file will be moved into a
        subdirectory called label in the input folder. This is an alternative to _copy_image, which is not
        yet used, function would need to be replaced above.
        :param input_path: Path of the original image
        :param label: The label
        """
        root, file_name = os.path.split(self.df.sorted_in_folder[ind])
        # two lines below check if the filepath contains as an ending a folder with the name of one of the labels
        # if so, this folder is being cut out of the path
        if os.path.split(root)[1] in labels:
            root = os.path.split(root)[0]
#         output_path = os.path.join(root, label, file_name)
        output_path = self.label_dir + '/' + label + '/' + file_name
        print("file_name =",file_name)
        print(" %s --> %s" % (file_name, label))
        move(self.df.sorted_in_folder[ind], output_path)
            
        # keep track that the image location has been changed by putting the new location-path in sorted_in_folder    
        self.df.loc[ind,'sorted_in_folder'] = output_path
        
        #####
        
    def make_folder(self):
        """
        Make folder if it doesn't already exist :param directory: The folder destination path.
        User can enter this block only once for the creation of folders during a single run time.
        Preferable to this at the beginning of the move.
        """
        
        if ImageGUI.label_flag < 1:
           self.label_dir = tk.filedialog.askdirectory(title = "Select Label Directory for image data")
           print(self.label_dir)
           for label in labels:
               if not os.path.exists(os.path.join(self.label_dir, label)):
                   os.makedirs(os.path.join(self.label_dir, label))
                   print(os.path.join(self.label_dir, label))
           ImageGUI.label_flag += 1
            
#### E2E Conversion
# This part represents the  E2E Conversion part.
# Select the Destination Folder first. Upon selecting the Source Folder, the conversion process on the all
# files present in the Source Folder will start and all of them will be extracted as image files in the destination folder
        
    def DestDialog(self):
        """
        Destination Directory for E2E-Jpg conversion.

        Returns
        -------
        None.

        """
        self.dest_dir = tk.filedialog.askdirectory(title = "Select Destination Directory for image data")
        
        
    def FileDialog(self):
        """
        Source directory containing E2E files for conversion into Jpg/Image slices.

        Returns
        -------
        None.

        """
        
        if ImageGUI.e2e < 1:
                       
            self.source_directory = tk.filedialog.askdirectory(title = "Select Directory with E2E data")
            status = 'Processing'
            self.convert_status.configure(text = ('Coverter Status = %s ' %(status)))
            print(self.source_directory)
        
            if self.dest_dir == 'None':
                print("Please select Destination Directory")
            else:
                 files = converter(self.source_directory, self.dest_dir)
                 
            #Update Completion Status    
            status = 'Completed'
            self.convert_status.configure(text = ('Coverter Status = %s ' %(status)))
            ImageGUI.e2e += 1

        
if __name__ == "__main__" :
# Start the GUI
    root = tk.Tk()
    app = ImageGUI(root)
    root.mainloop()    