from setuptools import setup

setup(
    name='ultimate',
    version='0.0.1',
    description='',
    author='Tolga Demirdal',
    url='https://github.com/shadymeowy/ultimate-gcs',
    setup_requires=[],
    install_requires=[
        'PySide6',
        'numpy',
        'pyqtgraph',
        'PyOpenGL',
        'opencv-python',
        'pyserial',
        'crcmod',
        'bingtiles @ git+https://github.com/shadymeowy/python-bingtiles',
        'QPrimaryFlightDisplay @ git+https://github.com/shadymeowy/QPrimaryFlightDisplay',
    ],
    packages=['ultimate', 'ultimate.assets'],
    entry_points={
        'console_scripts': [
            'ultimate = ultimate.__main__:main',
        ],
    },
    extras_require={
    },
    package_data={
        'ultimate': ['assets/*.png'],
        'ultimate': ['assets/*.ico'],
    },
    include_package_data=True,
)
