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
      'numpy~=1.24.3',
      'plotly~= 5.15.0',
      'pandas~= 2.0.3',
      'fire~= 0.5.0',
      'gudhi~= 3.7.1',
      'giotto-tda~= 0.6.0',
      'pytest>=8.0.1',
      'networkx~= 3.0',
      'icecream~= 2.1.3',
      'orjson~= 3.8.10',
      'joblib~= 1.2.0',
      'dionysus~= 2.0.9',
      'tqdm~= 4.64.1',
      'pympler~= 1.0.1',
      'lz4~= 4.3.2',
      'cpes @ git+https://github.com/Commutative-Ladders/cpes.git',
      'fzzpy @ git+https://github.com/CommutativeGrids/fzzpy.git',
      'chromatic_tda~=1.0.8',
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
      packages=find_packages(),
      package_data={
            'commutazzio': ['compute/data/*',
                            'statistics/weights/weights_0_to_10.npy',
                            'config.ini',
                            ]
      },
      )