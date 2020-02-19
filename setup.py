# encoding: utf-8


from setuptools import setup, find_packages
from codecs import open
from os import path


with open(path.join(path.abspath(path.dirname(__file__)), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='''ckanext-dataoverheid''',
    version='2.1.0',
    description='''The CKAN extension that implements the DCAT-AP-DONL metadata standard into CKAN as well as specific 
                   extra features which are part of the data.overheid.nl application.''',
    long_description=long_description,
    url='https://github.com/dataoverheid/ckanext-dataoverheid/',
    author='''Willem ter Berg''',
    author_email='''w.terberg@textinfo.nl''',
    license='CC0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: CC0',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='''ckan, extension, plugin, donl, textinfo, data, dataoverheid, koop, overheid, dcat, dcat-ap-donl, rdf''',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    namespace_packages=['ckanext'],
    install_requires=[],
    include_package_data=True,
    package_data={},
    data_files=[],
    entry_points='''
        [ckan.plugins]
        donl-scheme=ckanext.dataoverheid.plugins:SchemaPlugin
        donl-authorization=ckanext.dataoverheid.plugins:AuthorizationPlugin
        donl-rdf=ckanext.dataoverheid.plugins:RDFPlugin
        donl-interface=ckanext.dataoverheid.plugins:InterfacePlugin
    '''
)
