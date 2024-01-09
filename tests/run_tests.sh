# List of test files
test_files=(
    test_clfiltration.py
    test_commutative_ladder_quiver.py
    test_nScores.py
    test_random_model.py
    test_simplextree.py
    test_cPD.py
    test_cldatabase.py
    test_zigzagFiltration.py
)

# Loop over each test file and run pytest -s
for file in "${test_files[@]}"; do
    echo "Running tests in $file"
    pytest -s $file
    echo "Finished tests in $file"
    echo "------------------------"
done

echo "All tests completed."