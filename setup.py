from setuptools import setup
import sys

if sys.version_info < (3,5):
    sys.exit('Sorry, Python < 3.5 is not supported')

def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='localizer',
    version='0.1',
    description="Signal Localizer: Data Gathering Tool for Radiolocation",
    long_description=readme(),
    url='https://github.com/elBradford/localizer',
    author='Bradford',
    packages=['localizer'],
    install_requires=[
        'RPi.GPIO',
        'pyshark',
        'gpsd-py3',
    ],
    entry_points={
        'console_scripts': ['localizer=localizer.main:main'],
    },
    classifiers=[
        "Environment :: Console",
        "Operating System :: Unix",
        "Topic :: Scientific/Engineering"
    ],
    )