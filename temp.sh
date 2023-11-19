#!/bin/bash

libraries=(
    'matplotlib'
    'plotly'
    'pandas'
    'fire'
    'gudhi'
    'giotto-tda'
    'pytest'
    'networkx'
    'icecream'
    'orjson'
    'joblib'
    'dionysus'
    'tqdm'
    'pympler'
    'lz4'
    'numba'
)

for lib in "${libraries[@]}"; do
    version=$(pip show "$lib" | grep -i "version:" | awk '{print $2}')
    echo "'$lib~= $version',"
done
