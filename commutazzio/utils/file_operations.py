import os
from datetime import datetime
from time import sleep
import pickle
import json
import uuid


def create_directory(new_dir):
        if not os.path.isdir(new_dir):
            os.makedirs(new_dir)
            print(f"Directory {os.path.split(new_dir)[-1]} created.")
            #print("\n")
        #print(f"Saving to folder {os.path.split(new_dir)[-1]}.")



def read_data(directory,file_format="json"):
    """
    read all data from json files in directory data
    """
    data=[]
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(f".{file_format}"):
            with open(os.path.join(directory,filename), 'r') as fp:
                lines = (line.rstrip() for line in fp)
                file_data=[json.loads(line) for line in lines]
                data.extend(file_data)
    return data


def filepath_generator(dirname='./',filename=None,extension=None,overwrite=False):
    """
    Generate a filename with a given name and extension.
    If the file exists, append datetime to the provided name
    """
    if not os.path.isdir(dirname):
        raise FileNotFoundError(f"{dirname} does not exist.")
    if filename is None:
        filename=f'{datetime.now().strftime("%Y%m%d_%H%M%S")}_{uuid.uuid4().hex[-5:]}'
    if '.' in filename and extension is None:
        extension=filename.split('.')[-1]
        filename='.'.join(filename.split('.')[:-1])
    if 'extension' not in locals():
        raise ValueError("extension of the file not defined.")
    file_path=os.path.join(dirname,f"{filename}.{extension}")
    original_file_path=file_path
    count=1
    while os.path.isfile(file_path):
        if overwrite is True:
            print(f"Overwrite mode is on. Rewriting to {file_path} .")
            return file_path
        #file_path=os.path.join(dirname,f"{name}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')}.{extension}")
        file_path=os.path.join(dirname,f"{filename}_{str(count).zfill(6)}.{extension}")
        sleep(1e-6)
        count+=1
        if count>=1e5:
            raise FileExistsError(f"{file_path} already exists. Cannot create a new file with an ordinal (within 100k) attached to the original name.")
    if count==1:
        print(f"Saving to {file_path}")
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

def clean(directory):
    """delete all files in a folder"""
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        delete_file(file_path)

def delete_file(file_path):
    try:
        if os.path.isfile(file_path):
            os.unlink(file_path)
    except Exception as e:
        print(e)




def clean_all():
    clean('layered_point_cloud')
    clean('filtration')
    clean('pickles')
    clean('point_cloud')