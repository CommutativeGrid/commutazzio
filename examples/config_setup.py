import configparser
from pathlib import Path
import fire
import importlib.util

def get_package_path(package_name):
    """
    Get the path of a package without importing it.

    Args:
    - package_name (str): The name of the package.

    Returns:
    - Path: The path to the package directory.
    """

    # Find the spec of the package
    package_spec = importlib.util.find_spec(package_name)

    if package_spec is None:
        raise ImportError(f"Package {package_name} not found")

    # The package path is the parent directory of the __init__.py file
    package_path = Path(package_spec.origin).parent

    return package_path

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
            directory = Path(directory).absolute()
            # raise ValueError("Please provide an absolute path for the directory.")
        
        # Get the location of the config.ini in the package commutazzio
        
        package_dir = get_package_path("commutazzio")
        config_path = package_dir / 'config.ini'
        
        # If config.ini doesn't exist, create it
        if not config_path.exists():
            with config_path.open('w') as configfile:
                configfile.write('[storage]\n')
                configfile.write('precomputed_intv_dir = \n')
    
        # Read the existing config
        config = configparser.ConfigParser()
        config.read(config_path)
    
        # Set the directory
        config['storage']['precomputed_intv_dir'] = f"'{directory}'"
    
        # Write the updated config
        with config_path.open('w') as configfile:
            config.write(configfile)

        print(f"config_path:{config_path}")
    
        print(f"precomputed_intv_dir updated to: {directory}")

if __name__ == "__main__":
    fire.Fire(CommutazzioConfig)
