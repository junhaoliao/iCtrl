# libugremote

**UG_Remote Backend**

Refactoring in progress...

## Required Tools
Only Windows users will need to install these manually. If you are on Mac, simply type this in a Terminal:
<code>sudo xcode-select --install</code>
1. Python 3.9 or higher: https://www.python.org/downloads/
2. Git: https://git-scm.com/

(Optional) PyCharm: https://www.jetbrains.com/pycharm/download/

## Dependency Setup
If you are using PyCharm, you can simply clone this project by clicking on "Get from VCS" on the welcome page. You will 
then be prompted to set up a virtual environment and install the dependencies in requirement.txt automatically. 

If you prefer the command lines, type these in a Terminal:
```
# clone the project
git clone https://github.com/junhaoliao/libugremote.git

# change directory into the project directory
cd libugremote

# create a virtual enviroment under ProjectDirectory/venv for the Python project
python3 -m venv venv

# activate the virtual environment: choose only one from below
# (Windows) 
./venv/bin/activate
# (Mac)
source venv/bin/activate
 
# install the Python dependecies
pip install -r requirements.txt
```