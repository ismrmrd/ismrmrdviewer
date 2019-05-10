from setuptools import setup

setup(
    name='ismrmrd-viewer',
    version='0.0.1',
    packages=['ismrmrd-viewer'],
    package_dir={'ismrmrd-viewer': 'src'},
    license='LICENSE.txt',
    author='Kristoffer Langeland Knudsen',
    author_email='kristofferlknudsen@gradientsoftware.net',
    description='Simple tool for viewing ISMRMRD data.',
    scripts=['src/ismrmrd-viewer']
)
