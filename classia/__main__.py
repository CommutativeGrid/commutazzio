import fire
from . import Pipeline

if __name__ == '__main__':
  fire.Fire(Pipeline)
  # in package
  #python -m classia --crystal_type "fcc" --start 1 --end 6 --survival_rates "[0.5, 1]" --dim 1 --lattice_layer_size 5 --ladder_length 10 plot --title test_from_cli --file "./ttt.html" --overwrite "False"