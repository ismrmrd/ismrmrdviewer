# ISMRMRD Viewer

ISMRMRDVIEWER is a python package to view ISMRMRD/MRD (vendor agnostic MRI data format) raw data (including xml, data, waveforms and trajectories) and images.

# Installation
## MACOS/LINUX

Using venv:

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

You may need to manually download the test datasets in res/.

# Usage
## Start UI

### MACOS/LINUX/WINDOWS with venv
```bash
. venv/bin/activate
python3 ismrmrdviewer
```

## In UI
- File>Open
- Image series can be animated, and interactively windowed
- Raw data can be indivudually, or selected in multiples

## Exit
- Close UI
- Leave venv
(MACOS/LINUX/WINDOWS with venv)
```bash
deactivate
```


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.
