# Ethereum Validator Updater
Easily update execution, consensus, and mevboost clients to the latest versions in a single click using this update tool.

The script is adapted from Somer Esat's guides and makes maintaining a validator simple and accessible.

### Validator Updater (GUI):
![Screenshot from 2024-01-16 16-50-40](https://github.com/accidental-green/validator-update/assets/72235883/c2718fb3-8c97-4a93-aa2e-7d49bb4a5cec)

## Features:

- **Multi-client Support**: Update all major clients including Geth, Besu, Nethermind, Teku, Nimbus, Lighthouse, Prysm, and Mevboost.
- **Standard Configuration**: Get the same results as manually following Somer's update guides
- **GUI & CLI Versions**: Choose the version that suits your comfort level and setup.

## Prerequisites:


**Update system and install packages:**

`sudo apt-get update && sudo apt-get install git curl -y && sudo pip install requests`

**Clone the repository:**

`git clone https://github.com/accidental-green/validator-updater.git`

## Update Instructions:
Note: Choose either GUI (display) or CLI (terminal). Program starts upon running one of these commands:

**GUI Version:**

`python3 validator-updater/validator_updater_gui.py`

**or CLI Version:**

`python3 validator-updater/validator_updater_cli.py`

### Validator Update (GUI):

Make selections and click "Update". The GUI window will close and updates will proceed in the terminal.


![Screenshot from 2024-01-16 16-50-40](https://github.com/accidental-green/validator-update/assets/72235883/c2718fb3-8c97-4a93-aa2e-7d49bb4a5cec)


### Successful Update:

![Screenshot from 2024-01-16 17-11-12](https://github.com/accidental-green/validator-update/assets/72235883/c1f0f984-29d7-47b9-a982-1c31269cde02)


Once the updates have completed (~1 minute), you can restart the clients and begin running the new versions.

### Update Steps (CLI):

If you prefer to run the CLI version, the update will look like this:


![image](https://github.com/accidental-green/validator-update/assets/72235883/815da101-3077-4a56-afc8-98bec9a1372b)


## Important Note:

This project is open source but has not been audited. It is still relatively untested, so please use caution.

## Credits:

Many thanks to [Somer Esat](https://github.com/SomerEsat/ethereum-staking-guides) for creating the staking guides which served as the basis for this project.
