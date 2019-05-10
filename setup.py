from setuptools import setup

setup(
    name='ismrmrd-viewer',
    version='0.0.2',
    packages=['ismrmrd-viewer'],
    package_dir={'ismrmrd-viewer': 'src'},
    license='LICENSE.txt',
    author='Kristoffer Langeland Knudsen',
    author_email='kristofferlknudsen@gradientsoftware.net',
    description='Simple tool for viewing ISMRMRD data.',
    entry_points={'gui_scripts' : [ 'ismrmrd-viewer=viewer:main']},
    install_requires=[
        'cycler',
        'h5py',
        'ismrmrd',
        'kiwisolver',
        'matplotlib',
        'numpy',
        'pyparsing',
        'PySide2',
        'python-dateutil',
        'PyXB',
        'shiboken2',
        'six'
    ]
)
