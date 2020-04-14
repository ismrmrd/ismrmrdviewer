from setuptools import setup,find_packages

setup(
    name='ismrmrdviewer',
    version='0.1.0',
    packages=find_packages(),
    license='LICENSE.txt',
    author='Kristoffer Langeland Knudsen',
    author_email='kristofferlknudsen@gradientsoftware.net',
    description='Simple tool for viewing ISMRMRD data.',
    entry_points={'gui_scripts' : [ 'ismrmrdviewer=ismrmrdviewer.__main__:main']},
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
