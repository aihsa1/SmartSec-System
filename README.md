# SmartSec - A Smart Security System
## Made by Ran David
------------------------------------

# Description
This is a smart security application to detect pistols and manage incidents from different cameras.

------------------------------------

# Main Features
* Detecting pistols using a custom-trained ML model
* Grouping detections in a central server and logging incidents in database
* Live video feed + positive detection visualizations in the central server
* AES and RSA encrypted data transmission
* Reading and viewing past incidents from the DB

------------------------------------
# Demo GIFs and Images

### client:
![client](https://github.com/aihsa1/SmartSec/blob/master/RepoImages/client.png)

### server:
![server](https://github.com/aihsa1/SmartSec/blob/master/RepoImages/server.png)

### DB view mode:
![DB](https://github.com/aihsa1/SmartSec/blob/master/RepoImages/DB.png)

### Incident view in DB view mode:
![DB_popup](https://github.com/aihsa1/SmartSec/blob/master/RepoImages/DB_popup.png)

------------------------------------

# Installation Guide
* Install Python 3.9 using [this link](https://www.python.org/downloads/#:~:text=Release%20Notes-,Python%203.9.7,-Aug.%2030%2C%202021). Make sure you install pip
* Install [Visual Studio](https://visualstudio.microsoft.com/#:~:text=Visual%20Studio%20family-,Visual%20Studio,-Version%2017.1) with "Desktop development for C++"
* Install [Microsoft c++ Redistributable](https://docs.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170#:~:text=https%3A//aka.ms/vs/17/release/vc_redist.x86.exe)
* Create an virtual environment: ```python -m venv .venv```
* activate the virtual environment: ```".venv/scripts/activate"```
* Install jupyterlab: ```pip install jupyterlab```
* Enter jupyterlab: ```jupyter-lab```
* Run all of the commands in the [installations.ipynb notebook](https://github.com/aihsa1/SmartSec/blob/master/installations.ipynb)
* Create a MongoDB atlas instance and modify the PyMongoInterface.py file to fit your needs. This is done in order to send updates to the DB.
* Modify the destination address in the client.py file to the address of the server.
* NOTE: Make sure to activate the virtual environment before you run the project

# User Guide
* run the server using ```python server_multi_cam.py``` on the desired machine
* run clients using ```python client.py```

# Notes
* This system was not developed for production use, nor to be user-friendly. I'm sharing this code to publish a POC of what it would be to create a autonomous system that uses ML to complete a tedious instead of humans
* I'm not a CS professor, not a Data Scientis - The ML model I developed is the best I could achieve regarding my limited knowledge in ML, but it functions at a reasonable level. I used this project as an opportinuty to learn about ML and to further improve my skills (and also for fun :))
* This system may still have minor changes. No more functional changes will be made
