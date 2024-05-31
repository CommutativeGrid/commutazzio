FROM ubuntu:22.04

# DEBIAN_FRONTEND=noninteractive is used to prevent installation of
# package tzdata to ask for timezone
ENV DEBIAN_FRONTEND=noninteractive

ENV WORKDIR_PATH="/"
#"/usr/src"
WORKDIR $WORKDIR_PATH

# Required for Gudhi compilation
RUN apt update && apt install -y \
    make \
    g++ \
    cmake \
    cmake-curses-gui \
    graphviz \
    perl \
    texlive-bibtex-extra \
    biber \
    libboost-all-dev \
    libeigen3-dev \
    libgmp3-dev \
    libmpfr-dev \
    libtbb-dev \
    libcgal-dev \
    locales \
    python3.11 \
    python3.11-dev \
    python3.11-venv \
    python3-pip \
    python3-pytest \
    python3-tk \
    # python3-pybind11 \
    libfreetype6-dev \
    pkg-config \
    curl \
    clang \
    llvm \
    git \
    build-essential \
    mesa-common-dev \
    mesa-utils \
    freeglut3-dev \
    ninja-build

# Install pip for Python 3.11
RUN curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
    && python3.11 get-pip.py

# Set Python 3.11 as default and create aliases for python and pip
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 \
    && update-alternatives --install /usr/bin/pip3 pip3 /usr/local/bin/pip3.11 1 \
    && update-alternatives --install /usr/bin/pip pip /usr/local/bin/pip3.11 1 \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1

# Install pybind11
RUN pip3 install pybind11

ADD install_cgal.sh $WORKDIR
RUN sh install_cgal.sh

# Install vtk
RUN git clone --recursive https://gitlab.kitware.com/vtk/vtk.git \
    && cd vtk \
    && mkdir build \
    && cd build \
    && cmake -GNinja -DVTK_WHEEL_BUILD=ON -DVTK_WRAP_PYTHON=ON ../ \
    && ninja -j2 \
    && python3 setup.py install \
    && cd 

# Set library path for vtk dynamically
RUN find / -name "libvtkWrappingPythonCore3.11.so" -exec dirname {} \; | head -n 1 > /tmp/vtk_lib_path && \
    if [ -s /tmp/vtk_lib_path ]; then \
        echo 'export LD_LIBRARY_PATH=$(cat /tmp/vtk_lib_path):$LD_LIBRARY_PATH' >> /etc/profile.d/vtk.sh; \
    else \
        echo "VTK library path not found!" && exit 1; \
    fi

# Source the profile to set the environment variable
RUN echo 'source /etc/profile.d/vtk.sh' >> ~/.bashrc

# Install Python packages
RUN pip3 install \
    numpy \
    matplotlib \
    scipy \
    Cython \
    POT \
    scikit-learn

# apt clean up
RUN apt-get autoremove && rm -rf /var/lib/apt/lists/*

ARG GUDHI_VERSION="3.9.0"

RUN curl -LO "https://github.com/GUDHI/gudhi-devel/releases/download/tags%2Fgudhi-release-${GUDHI_VERSION}/gudhi.${GUDHI_VERSION}.tar.gz" \
&& tar xf gudhi.${GUDHI_VERSION}.tar.gz \
&& cd gudhi.${GUDHI_VERSION} \
&& mkdir build && cd build && cmake -DCMAKE_BUILD_TYPE=Release -DWITH_GUDHI_PYTHON=OFF -DPython_ADDITIONAL_VERSIONS=3 ..  \
&& make all test install \
&& cmake -DWITH_GUDHI_PYTHON=ON . \
&& cd python \
&& python3 setup.py install

# Clone and install fzzpy
RUN git clone --recursive https://github.com/CommutativeGrids/fzzpy.git \
&& cd fzzpy \
&& pip install .

# Clone and install cpes
RUN git clone https://github.com/CommutativeGrids/cpes.git \
&& cd cpes \
&& python -m pip install .

# Clone and install giotto-tda

# pyflagser
RUN git clone https://github.com/giotto-ai/pyflagser.git \
&& cd pyflagser \
&& python -m pip install .

# Clone giotto-ph and replace turf directory
RUN git clone --recursive https://github.com/CommutativeGrid/giotto-ph.git \
&& cd giotto-ph \
&& git submodule sync --recursive \
&& git submodule update --init --recursive --remote \
&& python -m pip install .

# giotto-tda
RUN git clone https://github.com/giotto-ai/giotto-tda.git \
&& cd giotto-tda \
&& pip install .

# Clone and install commutazzio
RUN git clone https://github.com/CommutativeGrids/commutazzio.git \
&& cd commutazzio \
&& pip install .

# Install jupyter notebook
RUN pip install jupyter
