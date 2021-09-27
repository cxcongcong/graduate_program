A demo for this website is shown in the link:
https://drive.google.com/file/d/1sD2vB02KR6B7s_0MoNIl_56zYKBI7d0f/view?usp=sharing



# The system will be run under UNSW VLAB environment

# Firstly, create a directory for the project and change direct to it
$ mkdir <target directory>
$ cd <target directory>

# Then download zipped file to <target directory> and upzip it
$ unzip <filename>

# Before running the system, the environment should be setup
$ cd <target directory>
$ python3 -m venv venv 
$ source venv/bin/activate 
$ pip install Flask 
$ pip install flask_migrate 
$ pip install flask_login 
$ pip install flask_wtf 
$ pip install email-validator 
$ pip install --upgrade setuptools 
$ pip3 install --upgrade pip 
$ pip install opencv-python

# Now you can start the system by running the following commands
$ cd <target directory>
$ source venv/bin/activate 
$ flask run

# Open the Google Explorer and go to 127.0.0.1/5000 to open the homepage.

# Note: Please use Google Explorer!
