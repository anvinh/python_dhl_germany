from setuptools import setup, find_packages
from codecs import open
from os import path


here = path.abspath(path.dirname(__file__))

long_description = ''
if path.isfile('README.md'):
    with open(path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()

requirements = []
if path.isfile('requirements.txt'):
    with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
        requirements = [line.strip() for line in f]

setup(
    name='python_dhl_germany',
    version='0.3.4.8',
    description='',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='',
    author='Johannes Eimer Production (JEP)',
    author_email='info@jep-dev.com',
    license='MIT',
    url='',
    packages=find_packages(exclude=['contrib', 'docs', 'tests', "tests*"]),
    data_files=[('', [
        'dhl/wsdl/3.4.0/geschaeftskundenversand-api-3.4.0-schema-bcs_base.xsd',
        'dhl/wsdl/3.4.0/geschaeftskundenversand-api-3.4.0-schema-cis_base.xsd',
        'dhl/wsdl/3.4.0/production.wsdl',
        'dhl/wsdl/3.4.0/test.wsdl',
    ])],
    include_package_data=True,
    install_requires=requirements,
    python_requires='>=3.9'
)
