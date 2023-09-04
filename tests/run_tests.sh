#!/bin/bash

# List of all test files
test_files=("test_nScores.py" "test_zigzagFiltration.py" "test_simplextree.py" "test_random_model.py" "test_commutative_ladder_quiver.py" "test_clfiltration.py" "test_cldatabase.py" "test_cPD.py")

for ((i=0; i<${#test_files[@]}-4; i++)); do
    for ((j=i+1; j<${#test_files[@]}-3; j++)); do
        for ((k=j+1; k<${#test_files[@]}-2; k++)); do
            for ((l=k+1; l<${#test_files[@]}-1; l++)); do
                for ((m=l+1; m<${#test_files[@]}; m++)); do
                    echo "Running tests with ${test_files[i]}, ${test_files[j]}, ${test_files[k]}, ${test_files[l]}, and ${test_files[m]}"
                    pytest ${test_files[i]} ${test_files[j]} ${test_files[k]} ${test_files[l]} ${test_files[m]}
                    echo -e "\n\n"  # Add some spacing between test runs for clarity
                done
            done
        done
    done
done
