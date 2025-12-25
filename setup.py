from setuptools import setup, find_packages
from os import path

with open(path.join(path.abspath(path.dirname(__file__)), 'mx_exporter/README.md'), encoding='utf-8') as f:
    detail_description = f.read()

setup(
    name='mx-exporter',
    version='2.2.6',
    author='Metax Developers',
    author_email="support-sw@metax-tech.com",
    description='MetaX prometheus data exporter',
    long_description=detail_description,
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        "Operating System :: OS Independent",
        'Topic :: System :: Monitoring'
    ],
    packages=find_packages(),
    include_package_data=True,
    package_data={'mx_exporter': ['./*']},
    python_requires=">=3.0",
    install_requires=[
        'prometheus_client>=0.7.0',
        'grpcio',
        'protobuf>=3.12.0'
    ],
    entry_points={
        'console_scripts': [
            'mx-exporter=mx_exporter:main',
        ],
    },
)
