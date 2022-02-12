import os
from datetime import datetime
from time import sleep
import pickle


def create_directory(new_dir):
        if not os.path.isdir(new_dir):
            os.makedirs(new_dir)
            print(f"Directory {os.path.split(new_dir)[-1]} created.")
            print("\n")
        #print(f"Saving to folder {os.path.split(new_dir)[-1]}.")

def filepath_generator(dirname,name,suffix=None,overwrite=False):
    """
    Generate a filename with a given name and suffix.
    If the file exists, append datetime to the provided name
    """
    if not os.path.isdir(dirname):
        raise FileNotFoundError(f"{dirname} does not exist.")
    if '.' in name and suffix is None:
        suffix=name.split('.')[-1]
        name='.'.join(name.split('.')[:-1])
    if 'suffix' not in locals():
        raise ValueError("Suffix of the file not defined.")
    file_path=os.path.join(dirname,f"{name}.{suffix}")
    original_file_path=file_path
    count=1
    while os.path.isfile(file_path):
        if overwrite is True:
            print(f"Overwrite mode is on. Rewriting to {file_path} .")
            return file_path
        #file_path=os.path.join(dirname,f"{name}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')}.{suffix}")
        file_path=os.path.join(dirname,f"{name}_{str(count).zfill(2)}.{suffix}")
        sleep(1e-6)
        count+=1
        if count>=100:
            raise FileExistsError(f"{file_path} already exists. Cannot create a new file with random file name.")
    if count==1:
        print(f"Saving to {file_path}.")
    else:
        print(f"File {original_file_path} already exists. Saving to {file_path}.")
    return file_path

def filename_logger(obj,filename):
    """
    Log the filename and important information to a file.
    """
    with open('./pickles/files.log','a') as f:
        f.write(f"{filename}\n")


def pickle_save(obj,file_path=None):
    """
    Save an object to a pickle file.
    """
    create_directory('./pickles')
    key_list=['crystal_type','survival_rates','dim','lattice_layer_size','ladder_length']
    parameters=obj.compute_engine.parameters
    if file_path is None:
        fn=''
        fn+=parameters['crystal_type']+'_'
        fn+=f"atoms_{parameters['lattice_layer_size']**3}_length_{parameters['ladder_length']}_"
        fn+=f"dimension_{parameters['dim']}_"
        fn+=f"sr_{parameters['survival_rates'][0]}_{parameters['survival_rates'][1]}"
        fn+=".pkl"
        file_path=fn
    fp=filepath_generator('./pickles',file_path,overwrite=False)
    filename_logger(obj,fp)
    with open(fp,'wb') as f:
        pickle.dump(obj,f)

def pickle_load(file_path=None):
    """
    Load an object from a pickle file.
    If file_path is none, load the latest pickle file recorded in files.log.
    """
    if file_path is None:
        with open('./pickles/files.log','r') as f:
            file_path=f.readlines()[-1].strip()
        print('Loading the latest pickle file.')
    with open(file_path,'rb') as f:
        obj=pickle.load(f)
    return obj

def pickle_load_latest(number):
    """
    Load the latest n pickle file recorded in files.log.
    """
    with open('./pickles/files.log','r') as f:
        fps=f.read().splitlines()[-number:]
    for fp in fps:
        yield pickle_load(fp)