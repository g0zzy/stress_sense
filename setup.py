import os
from setuptools import find_packages
from setuptools import setup

requirements = []

if os.path.isfile('requirements.txt'):
    with open('requirements.txt') as f:
        content = f.readlines()
    requirements.extend([x.strip() for x in content if 'git+' not in x])

setup(name='stress_sense',
    version="0.0.1",
    description="Stress detector and clusterer",
    packages=find_packages(),
    install_requires=requirements,
    test_suite='tests',
    # include_package_data: to install data from MANIFEST.in
    include_package_data=True,
    # scripts=['scripts/packagename-run'],
    zip_safe=False)
