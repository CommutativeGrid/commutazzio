import configparser
from pathlib import Path
import fire

class CommutazzioConfig:

    @staticmethod
    def set_precomputed_intv_dir(directory: str):
        """
        Set the directory for precomputed intervals in config.ini.
        
        Args:
        - directory (str): The absolute path to the directory.
        """
        
        # Ensure the provided path is absolute
        if not Path(directory).is_absolute():
            raise ValueError("Please provide an absolute path for the directory.")
        
        # Get the location of the config.ini within the package
        current_dir = Path(__file__).parent
        config_path = current_dir / 'config.ini'
        
        # If config.ini doesn't exist, create it
        if not config_path.exists():
            with config_path.open('w') as configfile:
                configfile.write('[storage]\n')
                configfile.write('precomputed_intv_dir = \n')
    
        # Read the existing config
        config = configparser.ConfigParser()
        config.read(config_path)
    
        # Set the directory
        config['storage']['precomputed_intv_dir'] = directory
    
        # Write the updated config
        with config_path.open('w') as configfile:
            config.write(configfile)
    
        print(f"precomputed_intv_dir updated to: {directory}")

if __name__ == "__main__":
    fire.Fire(CommutazzioConfig)
