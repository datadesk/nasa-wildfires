import os
from setuptools import setup


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


setup(
    name='nasa-wildfires',
    version='0.0.2',
    description="Download wildfire data from NASA satellites",
    long_description=read('README.rst'),
    author='Los Angeles Times Data Desk',
    author_email='datadesk@latimes.com',
    url='http://www.github.com/datadesk/nasa-wildfires',
    license="MIT",
    packages=("nasa_wildfires",),
    entry_points="""
        [console_scripts]
        nasawildfires=nasa_wildfires.cli:cmd
    """,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: MIT License',
    ],
    project_urls={
        'Maintainer': 'https://github.com/datadesk',
        'Source': 'https://github.com/datadesk/nasa-wildfires',
        'Tracker': 'https://github.com/datadesk/nasa-wildfires/issues'
    },
)
