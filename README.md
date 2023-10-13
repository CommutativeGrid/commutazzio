# Commutazzio

**Commutazzio** is a python package for computing topological invariants of commutative ladders.

## Installation

TODO: 
1. prepare the requirements.txt file, 
2. prepare the conda environment yaml file.

`python3.10` is required for installing this module.

External dependencies:
* [dionysus2](https://mrzv.org/software/dionysus2/) (for computing persistent homology)
* [fzz](https://github.com/taohou01/fzz)

For installing dionysus2 (MacOS):
* brew install boost

```
git clone https://github.com/Commutative-Ladder/classia.git
```
then `cd` to the cloned foler, and
```
pip install .
```

To upgrade, run
```
pip install . --upgrade
```

### Installation in user mode

If you do not have root access, you can install the package in user mode. This will install the package in a user-specific location, and it will not be available to other users on the system.

```
pip install --user .
```


### Installation in development (editable) mode

If you want to modify the source code, you can install the package in developement mode. This will create a link to the source code, so that any changes to the source code will be reflected in the installed package.

```
pip install -e .
```

### Precompute

```
commutazzio_precompute
```
#default m_threshold=80

```
commutazzio_precompute --m_threshold=100
```



## Basic usage

TBD