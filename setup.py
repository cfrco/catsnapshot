#from distutils.core import setup
from setuptools import setup

from catsnapshot import __version__

setup(
    name = 'catsnapsho',
    description = 'A tool using rsync to backup and manage in Python.',
    version = __version__,
    author = 'cfrco',
    author_email = 'z82206.cat@gmail.com',
    packages = ['catsnapshot'],
    entry_points = {
        'console_scripts':[
            'catsnapshot = catsnapshot.__cli__:main',  
        ],    
    },
)
