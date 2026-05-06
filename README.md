# MiniScopeInscopixConversion
A small collection of tools to convert Inscopix video files (.isxd) to avi files and back.

# Install
Created and tested on Windows 11. Instuctions are for Windows with PowerShell.
- you need Python in version 3.12
- clone repository with `git clone https://github.com/WinterLab-Berlin/MiniScopeInscopixConversion` or download it as zip
- change into the repository folder `cd MiniScopeInscopixConversion`
- create the virtual environment with python 3.12: `py -V:3.12 -m venv venv`
- to activate the virtual environment: `.\venv\Scripts\Activate.ps1`
- install all python packages: `pip install -r requirements.txt`
- make shure the ffmpeg.exe and fprobe.exe are installed on the system or placed in the folder. FFMPEG can be downloaded at https://ffmpeg.org/download.html

# Execute
Open the folder with the editor of your choice (e.g. Visual Studio Code)

## Convert Inscopix files
To convert inscopix video files (.isxd) to .avi files open "isdx_to_avi.py". Change parameters on the top. Run the file. It will also split the result file into equal .avi files.

## Convert avi to Inscopix
To convert .avi files to inscopix video file (.isxd) open "avi_to_isdx.py". Change the parameters on the top. Run the file.