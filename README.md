# Camélia

**Camélia** is a python package for computing topological invariants of commutative ladders.

~~It features a streamlined process from an user input of parameters of fcc/hcp lattice to decorated persistence diagram.~~

~~Using this module smoothly requires the installation of [random-cech](https://bitbucket.org/tda-homcloud/random-cech/src/master/) in the working directory. See [below](##Basic-usage) for details.~~

## Installation

`python3.10` is required for installing this module.

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

### Installation in developement (editable) mode

```
pip install -e .
```

## Basic usage

Many files will be generated during each running, so it is advised to create a new folder as the working directory. We recommend install [random-cech](https://bitbucket.org/tda-homcloud/random-cech/src/master/) as a subfolder in the workding directory, otherwise argument `executor` needs to be specified to the location of executable file `cech_filtration`.

During the execution, directory with name `point_cloud` and `filtration` will be created to store intermediate data.

In addition, folders `css` and `js` in `samples` need to be copied the working directory for using native Javascript codes to plot the persistence diagram. Although this is not necessary if only `plotly` is used.

Finally the working directory will have the following structure:

```
dir
|
+--random-cech
|
+--point_cloud
|
+--filtration
|
+--css
|
+--js
```

### Via CLI

While there is a long list of parameters, we have more customizability as an compensation. An example is given below, follows by detailed explanation of each parameters.

```shell
python -m classia --crystal_type "fcc" --start 1 --end 6 --survival_rates "[0.5, 1]" --dim 1 --lattice_layer_size 5 --ladder_length 10 plot --title "test_from_cli" --file "./ttt.html" --overwrite "False"
```

* `crystal_type`: Creates a lattice data with atom radius being 1. It accepts one of the following values.
  * `fcc`: face centerd cubic; 
  * `hcp`: hexagonal close packing.
* `start`: Starting radius of the Čech complex.
* `end`: Final radius of the Čech complex, intermediated values will be interploated linearly according to `ladder_length`.
* `survival_rates`: A list with two values specifying the survival rate in the lower row and upper row respectively.
* `dim`: Homology dimension to be used
* `lattice_layer_size`: Number of atoms along one coordinate. There will be in total `lattice_layer_size**3` atoms.
* `ladder_length`: Length of the commutative ladder. For CL(50) the input should be 50.

Parameters above specify our input data. Then the compute engine works and the output is used to plot a connected persistence diagram. Parameters after `plot` in the command line specifies the output.

* `title`: Title of the diagram. Can be ignored.
* `file`: File path of the generated html file. Can be ignored.
* `overwrite`: Whether or not to overwrite if a file with the same given name existed. If set to `False` and `file` is not given, then a random file name will be used. If set to `True` and `file` is not given, then `./test.html` will be used.

### Via executing a python script

A usage example is given in `./samples/compute_and_save.py` and `./samples/load_and_plot.py`. We recommend to pickle the result as in the file for later usage or changing plot styles as the computation can be very time-consuming.

### Native Javascript method

For native Javascript method using CLI, replace `plot` with `plot_js` and no parameter follows. Example:
```shell
python -m classia --crystal_type "fcc" --start 1 --end 6 --survival_rates "[0.5, 1]" --dim 1 --lattice_layer_size 5 --ladder_length 10 plot_js
```

The same is true if using python script.

Both ways will create a new Javascripte file with filename like `fcc_7_0.5_1_50.js`. Copy `./samples/visualization.html` to the working directory and change the source at line 11 to that filename accordingly.

### Host

Although it is possible to open the generated `html` file directly, we recommend using a simple localhost, for example running the following command in the working directory.

```python
python -m http.server 8000
```
Then open `http://localhost:8000/` in your browser.

## Issues

Internet connection is required to load `plotly.js` library via a cdn. If you want to work offline, pass `--include_plotlyjs 'True'` at the end of CLI or add it in the python script while plotting.