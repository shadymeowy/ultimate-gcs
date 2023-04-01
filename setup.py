from setuptools import setup

setup(
    name='ultimate-gcs',
    version='0.0.1',
    description='',
    author='Tolga Demirdal',
    url='https://github.com/shadymeowy/ultimate-gcs',
    setup_requires=[],
    install_requires=[],  # TODO
    packages=['ultimate'],
    entry_points={
        'console_scripts': [
            'ultimate = ultimate.__main__:main',
        ],
    },
    extras_require={
    },
)
