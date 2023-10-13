from commutazzio.compute import CommutativeGridPreCompute as CGPC
import pickle
from pathlib import Path
import time
from tqdm import tqdm
import argparse


class Precomputer:

    def __init__(self):
        ...

    def run(self,m_threshold):
        n = 2
        # Determine the absolute path of the current file
        current_file_path = Path(__file__).resolve()
        # Determine the absolute path of the desired directory
        dirname = current_file_path.parent / "precomputed_results"
        dirname.mkdir(exist_ok=True)

        start_times = []

        # Precompute the sum for the range up to m_threshold
        full_sum = sum([i**(2*n) for i in range(1, m_threshold+1)])
        remaining_sum = full_sum

        # Using tqdm to display progress bar
        for m in tqdm(range(1, m_threshold+1), desc="Processing"):
            start_time = time.time()

            a = CGPC(m, n)
            fn_intv = f"intv_{m:03d}_{n:03d}.pkl"
            fn_variables = f"variables_{m:03d}_{n:03d}.pkl"
            fp_intv = Path(dirname)/fn_intv
            fp_variables = Path(dirname)/fn_variables
            with open(fp_intv, "wb") as f:
                pickle.dump(a.get_intervals(), f)
            with open(fp_variables, "wb") as f:
                pickle.dump(a.get_variables(), f)

            end_time = time.time()
            duration = end_time - start_time
            start_times.append(duration)

            # Update c using the current iteration
            c = duration / (m**(2*n))

            # Subtract the current m term from the remaining sum
            remaining_sum -= m**(2*n)

            # Compute estimated time for remaining iterations using the latest c
            est_remaining_time = c * remaining_sum

            # Update tqdm's postfix to display the time taken, total time spent, and the estimated time remaining
            tqdm.write(f"Time taken for m={m}: {duration:.2f} seconds. Total time spent: {sum(start_times):.2f} seconds. Estimated time remaining: {est_remaining_time:.2f} seconds.")


def main():
    parser = argparse.ArgumentParser(description='Precompute data for Commutazzio.')
    parser.add_argument('--m_threshold', type=int, default=80, help='Threshold for m')
    args = parser.parse_args()
    precomputer = Precomputer()
    precomputer.run(m_threshold=args.m_threshold)

if __name__ == "__main__":
    main()