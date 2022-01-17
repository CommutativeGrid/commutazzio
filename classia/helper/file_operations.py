import os


def create_directory(new_dir):
        if not os.path.isdir(new_dir):
            os.makedirs(new_dir)
            print(f"Directory {os.path.split(new_dir)[-1]} created.")
            print("\n")
        print(f"Saving to folder {os.path.split(new_dir)[-1]}.")