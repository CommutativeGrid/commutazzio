# commutazzio

**commutazzio** is a Python package designed for computing topological invariants of commutative ladders specified in the paper [Refinement of Interval Approximations for Fully Commutative Quivers](https://arxiv.org/abs/2310.03649).

We are continually expanding our library with more examples and extensive documentation.

## Documentation

The documentation can be found at [https://commutativegrids.github.io/commutazzio/](https://commutativegrids.github.io/commutazzio/).

## Installation

This package is compatible with Python 3.10 and may not work correctly with earlier versions. To install `commutazzio`, please first install fzzpy as a prerequisite. Follow these steps for a smooth installation process:

1. **Install fzzpy:**

   Navigate to the [fzzpy GitHub repository](https://github.com/CommutativeGrids/fzzpy) and follow the instructions provided there.

2. **Install commutazzio:**

   After installing `fzzpy`, `commutazzio` can be installed using pip. Run the following command in your terminal:
   ```bash
   pip install --user .
   ```

## Quick Start

Several examples are provided in the `examples/` directory to help you get started with `commutazzio` for its different functionalities.

### Indecomposable Decomposition

This section is currently under development and will be updated shortly. 
(`examples/indecomposable_decomposition_CL(4).ipynb`)

### Connected Persistence Diagrams

For a practical demonstration of Connected Persistence Diagrams, please refer to the Jupyter notebook located at `examples/connected_persistence_diagrams.ipynb`. This notebook is designed to guide you through the process of plotting Connected Persistence Diagrams, as illustrated in Figure 14 of our research paper.

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
