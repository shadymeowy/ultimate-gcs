from setuptools import setup

setup(
    name='python-bing-tiles',
    version='0.0.1',
    description='Small library for accessing Bing Static Maps API',
    author='Tolga Demirdal',
    url='https://github.com/shadymeowy/python-bing-tiles',
    setup_requires=[],
    install_requires=[], # TODO
    packages=['bingtiles'],
    entry_points={
        'console_scripts': [
            'bingtiles = bingtiles.__main__:main',              
        ],          
    },
    extras_require={
        'processbar': ['tqdm'],
    },
)
 
