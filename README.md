# commutazzio

**commutazzio** is a Python package for computing topological invariants of commutative ladders specified in the paper [Refinement of Interval Approximations for Fully Commutative Quivers](https://arxiv.org/abs/2310.03649).

We are continually expanding our library with more examples and extensive documentation.

**Related projects:** See [rucpd](https://bitbucket.org/tda-homcloud/rucpd/src/main/) for a cPD computation software with improved integration with [homcloud](https://homcloud.dev/index.html).

## Documentation

The documentation can be found at [https://commutativegrid.github.io/commutazzio/](https://commutativegrid.github.io/commutazzio/).

## Installation

### Docker

The easiest way to get started with `commutazzio` is by using Docker. Below are the instructions to build and run a Docker container.

#### Build the Docker Image

To build the Docker image, run the following command in the root directory of the project:

```bash
docker build -t commutazzio -f docker/Dockerfile .
```

#### Run the Docker Container

You can run the Docker container in interactive mode.

Interactive Mode:

```bash
docker run -it commutazzio
```

#### Jupyter Notebook in VSCode

You can use Visual Studio Code (VSCode) to interact with the Jupyter notebooks in the Docker container. Follow the steps below to set this up:

1. Run the Docker Container:
   Run the docker in interactive mode above or run the following command to start the container in detached mode:

   ```bash
   docker run -d --name my-container commutazzio tail -f /dev/null
   ```

2. Attach VSCode to the Running Container:
   Follow the instructions provided in the [VSCode documentation](https://code.visualstudio.com/docs/devcontainers/attach-container) to attach to the running container.
3. Start Jupyter Notebook in the Container:
   Open a terminal in VSCode and run the following command to start the Jupyter server:

   ```bash
   jupyter notebook --ip 127.0.0.1 --port 8888
   ```

4. Access Jupyter Notebook via VSCode:
   Open a new `.ipynb` file in VSCode, click the button in the top right corner and select "Select Another Kernel…" and choose "Existing Jupyter Server..." to connect to the Jupyter server running inside the Docker container. The remote url will be `http://127.0.0.1` if you followed the instructions above and the password is the token provided in the terminal when you started the Jupyter server.

### Local Installation

This package is compatible with Python 3.11 and may not work correctly with earlier versions. To install `commutazzio`, please first install `fzzpy` as a prerequisite. Follow these steps for a smooth installation process:

1. **Install fzzpy:**

   Navigate to the [fzzpy GitHub repository](https://github.com/CommutativeGrids/fzzpy) and follow the instructions provided there.

2. **Install commutazzio:**

   After installing `fzzpy`, `commutazzio` can be installed using `pip`. Run the following command in your terminal:

   ```bash
   pip install --user .
   ```

## Quickstart

Several examples are provided in the `examples/` directory to help get started with `commutazzio` for its different functionalities.

### Indecomposable Decomposition

This section is currently under development and will be updated shortly. 
(`examples/indecomposable_decomposition_CL(4).ipynb`)

### Connected Persistence Diagrams

Interval approximations values required to plot a connected persistence diagram can be computed using the `CLInvariants` calss. We then provide two method to visualize it as depicted in the paper.

1. **Complementary triangles mode**

   The Jupyter notebook located at `./examples/connected_persistence_diagrams.ipynb` is designed to guide you through the process of plotting Connected Persistence Diagrams, as illustrated in Figure 14 of the paper.
   We note that in the default settings, the death coordinate is exclusive to avoid the overlapping of homology generators from the upper and the lower layer respectively on the diagonal line of the plot.

2. **Overlapping triangles mode**

   The notebook `./examples/silica_thinning.ipynb` shows how to plot the diagram as in Figure 20(b) in the paper. In this plot mode the death coordinate is inclusive.



### Use Precomputed Intervals for Faster Computations

For faster and more efficient computations, consider using precomputed intervals data. This approach can reduce the time spent on calculations. Here's how you can set it up:

First, navigate to the `./examples/` directory and execute the following command:

```bash
python precompute_intervals.py --m_threshold=80
```

In this command, `m_threshold` represents the maximum ladder length you're considering. Executing this will generate a `./precomputed_results/` directory right where `precompute_intervals.py` is situated.

Next, you'll need to update the `precomputed_intv_dir` parameter in the `config.ini` file, which is located in the root directory of `commutazzio`. This can be done by executing the command below:

```bash
python config_setup.py set_precomputed_intv_dir "./precomputed_results"
```

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE.md) file for details.
