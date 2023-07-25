# Validator Update
Open source tool to instantly update Execution and Consensus clients to the latests version.

To run the program, use the following commands:

`sudo apt-get update && sudo apt-get install git curl -y && sudo pip install requests`

`git clone https://github.com/accidental-green/validator-update.git`

`python3 validator-update/validator-update.py`

This will update to the latest version of the selected clients and print a confirmation at the end.

![image](https://github.com/accidental-green/validator-update/assets/72235883/2cf6a066-4505-4e99-ab9c-49b2e92cb15c)

That's it, everything is updated! Be sure to start the clients and verify you are attesting again.
