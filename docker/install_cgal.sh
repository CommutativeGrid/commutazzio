#!/bin/bash

# error management : https://dev.to/banks/stop-ignoring-errors-in-bash-3co5
set -ue

export CGAL_VERSION="5.4.1"

curl -LO "https://github.com/CGAL/cgal/releases/download/v${CGAL_VERSION}/CGAL-${CGAL_VERSION}.tar.xz"
tar xf CGAL-${CGAL_VERSION}.tar.xz
mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=Release ../CGAL-${CGAL_VERSION}/
make install
cd ..
rm -rf build CGAL-${CGAL_VERSION}