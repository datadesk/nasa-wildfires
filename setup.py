import os
from setuptools import setup


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


setup(
    name='nasa-wildfires',
    version='0.0.4',
    description="Download wildfire data from NASA satellites",
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    author='Ben Welsh',
    author_email='b@palewi.re',
    url='http://www.github.com/palewire/nasa-wildfires',
    license="MIT",
    packages=("nasa_wildfires",),
    install_requires=[
        "requests",
        "geojson",
        "click",
    ],
    entry_points="""
        [console_scripts]
        nasawildfires=nasa_wildfires.cli:cmd
    """,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: MIT License',
    ],
    project_urls={
        'Maintainer': 'https://github.com/palewire',
        'Source': 'https://github.com/palewire/nasa-wildfires',
        'Tracker': 'https://github.com/palewire/nasa-wildfires/issues'
    },
)
