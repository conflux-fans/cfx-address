from setuptools import setup, find_packages

VERSION = '0.0.3'
DESCRIPTION = 'Conflux base32 address'
LONG_DESCRIPTION = 'Used to convert hex to base32 address'

# Setting up
setup(
    # the name must match the folder name 'verysimplemodule'
    name="cfx-address",
    version=VERSION,
    author="The Conflux foundation",
    author_email="wangpan@conflux-chain.org",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[
        "eth-utils"
    ],  # add any additional packages that
    # needs to be installed along with your package. Eg: 'caer'

    keywords=['python', 'first package'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)