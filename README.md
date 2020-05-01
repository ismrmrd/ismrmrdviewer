# ISMRMRD Viewer

ISMRMRDVIEWER is a python package to view ISMRMRD/MRD (vendor agnostic MRI data format) raw data (including xml, data, waveforms and trajectories) and images.

# Installation
Using venv:

## MACOS/LINUX
```bash
git clone https://github.com/ismrmrd/ismrmrdviewer.git
cd ismrmrdviewer/
python3 -m venv venv
. venv/bin/activate
python3 setup.py --verbose install
deactivate
```
## WINDOWS
```cmd
git clone https://github.com/ismrmrd/ismrmrdviewer.git
cd ismrmrdviewer\
python3 -m venv venv
venv\bin\activate.bat
python3 setup.py --verbose install
deactivate
```
### Note!
You may need to manually download the test datasets in res/.

# Usage
## Start UI
- intialise venv
### MACOS/LINUX
```bash
. venv/bin/activate
```
### WINDOWS
```cmd
venv/bin/activate.bat
```
- run package
```bash
python3 ismrmrdviewer
```

## In UI
- File>Open
- Image series can be animated, and interactively windowed.
- Raw data lines can be browsed individually, or selected in multiples.

## Exit
- Close UI
- Leave venv
(MACOS/LINUX/WINDOWS with venv)
```bash
deactivate
```

# Contributing
Features are welcome.
For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.
