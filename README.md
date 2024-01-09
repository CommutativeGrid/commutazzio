# Commutazzio

Commutazzio is a Python package designed for computing topological invariants of commutative ladders.
Examples and documentation will be added soon.

## Installation

This package is compatible with Python 3.10 and may not work correctly with earlier versions. Before installing Commutazzio, you need to install `fzzpy`. Follow these steps for a smooth installation process:

1. **Install fzzpy:**

   Visit the [fzzpy GitHub repository](https://github.com/CommutativeGrids/fzzpy) and follow the instructions provided there to install `fzzpy`.

2. **Install commutazzio:**

   After installing `fzzpy`, `commutazzio` can be installed using pip. Run the following command in your terminal:
   ```bash
   pip install --user .
   ```

### Using Precomputed Intervals 

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
