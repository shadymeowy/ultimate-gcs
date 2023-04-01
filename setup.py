from setuptools import setup

setup(
    name='ultimate-gcs',
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
        'git+https://github.com/shadymeowy/python-bingtiles',
        'git+https://github.com/shadymeowy/QPrimaryFlightDisplay',
    ],
    packages=['ultimate'],
    entry_points={
        'console_scripts': [
            'ultimate = ultimate.__main__:main',
        ],
    },
    extras_require={
    },
)
