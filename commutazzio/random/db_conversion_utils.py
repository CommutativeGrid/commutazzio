import pandas as pd
import numpy as np
import csv

def sqlite_to_df_cl4_pc(db):
    """
    Convert SQLite database records to a pandas DataFrame for CL(4) filtrations generated using the Point Cloud Model.

    This function iterates over each record in the provided database, extracting specific
    information and organizing them into a structured DataFrame.

    Parameters
    ----------
    db : Database connection object
        The database connection from which to retrieve CL(4) filtration data.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the structured data from the CL4 filtration records.
        Columns include space dimension, homology dimension, number of points, critical radii number,
        ladder length, dots, lines, number of points removal, and decompositions.

    """
    # Defining the keys outside of the loop
    I_keys = [f"I{_}" for _ in range(1, 56)]
    N_keys = [f"N{_}" for _ in range(1, 22)]
    keys = ['space_dim', 'homology_dim', 'num_pts',\
             'critical_radii_number','ladder_length','dots','lines']
    rows = []
    for record in db.get_all():
        info=record.info
        row = {key: info.get(key) for key in keys}
        row |= {'num_pts_removal': len(info['vertical_removal'])}
        row |= {key: info['decomp'].get(key, 0) for key in I_keys + N_keys}
        rows.append(row)
    df = pd.DataFrame(rows)
    return df


def sqlite_to_df_cln_pc(db):
    """
    Convert SQLite database records to a pandas DataFrame for CL(n) filtrations generated using the Point Cloud Model.

    Similar to the CL4 conversion, this function processes records from a database containing
    CL(n) filtrations. Each record's information is extracted and compiled into a DataFrame.

    Parameters
    ----------
    db : Database connection object
        The database connection from which to retrieve CL(n) filtration data.

    Returns
    -------
    pandas.DataFrame
        A DataFrame representing the CL(n) database records.
        Columns include space dimension, homology dimension, number of points, critical radii number,
        ladder length, dots, lines, and number of points removed.

    """
    # Defining the keys outside of the loop
    keys = ['space_dim', 'homology_dim', 'num_pts',\
             'critical_radii_number','ladder_length','dots','lines']
    rows = []
    for record in db.get_all():
        info = record.info
        row = {key: info.get(key) for key in keys}
        row |= {'num_pts_removed': len(info['vertical_removal'])}
        rows.append(row)
    df = pd.DataFrame(rows)
    return df

import glob, os
from ..filtration import CLFiltrationDB

def collect_data_from_db_files(dirnames, fn_pattern, db_2_df):
    """
    Loop through all files in the directory of form "{fn_pattern}_*.db". For each file, 
    read the database by applying the provided function (db_2_df), which returns a DataFrame.
    All DataFrames are then combined into one DataFrame.

    Args:
        dirname (str): The directory containing the db files.
        fn_pattern (str): The filename pattern to match.
        db_2_df (function): Function to convert db data into DataFrame.

    Returns:
        DataFrame: The combined data from all matched db files.
    """
    all_data = pd.DataFrame()
    for dirname in dirnames:
        # Loop through all files in the directory matching the pattern
        for filename in sorted(glob.glob(os.path.join(dirname, f"{fn_pattern}*.db"))):
            print(f"Processing file: {filename}")
            new_db = CLFiltrationDB(filename, create_new_db=False)
            df_new = db_2_df(new_db)
            all_data = pd.concat([all_data, df_new], ignore_index=True)
            print(f"Finished processing file: {filename}")

    return all_data


