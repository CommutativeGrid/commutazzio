import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

VERSION = '0.5.0'
PACKAGE_NAME = 'commutazzio'
AUTHOR = '平岡研究室区間近似実用化チーム'
AUTHOR_EMAIL = 'xu.chenguang.k34@kyoto-u.jp'
URL = ''

LICENSE = 'MIT'
DESCRIPTION = 'Commutative ladder source-sink interval approximation'
LONG_DESCRIPTION = (HERE / "README.md").read_text(encoding='utf-8')
LONG_DESC_TYPE = "text/markdown"

CLASSIFIERS = [
      'Development Status :: 3 - Alpha',
      'License :: OSI Approved :: MIT License',
      'Intended Audience :: Science/Research',
      'Programming Language :: Python :: 3.10',
      'Topic :: Scientific/Engineering'
]

INSTALL_REQUIRES = [
      'numpy',
      'matplotlib',
      'plotly',
      'pandas',
      'fire',
      'gudhi',
      'giotto-tda',
      'pytest',
      'networkx',
      'icecream',
      'orjson',
      'joblib',
      'dionysus',
      'tqdm',
      'pympler',
      'lz4',
      'numba',
      'cpes @ git+https://github.com/Commutative-Ladders/cpes.git',
      'fzzpy @ git+https://github.com/CommutativeGrids/fzzpy.git',
]

DEPENDENCY_LINKS = [
      'https://github.com/CommutativeGrids/cpes.git',
      'https://github.com/CommutativeGrids/fzzpy.git',
]


setup(name=PACKAGE_NAME,
      version=VERSION,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      long_description_content_type=LONG_DESC_TYPE,
      classifiers=CLASSIFIERS,
      author=AUTHOR,
      license=LICENSE,
      author_email=AUTHOR_EMAIL,
      url=URL,
      install_requires=INSTALL_REQUIRES,
      dependency_links=DEPENDENCY_LINKS,
      packages=find_packages(),
      package_data={
            'commutazzio': ['compute/data/*',
                            'statistics/weights/weights_0_to_10.npy',
                            ]
      },
      entry_points={
          'console_scripts': [
              'commutazzio_precompute = commutazzio.compute.data.precompute_execution:main',
          ],
      },
      )