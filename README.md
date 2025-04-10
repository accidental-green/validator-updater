# Ethereum Validator Updater
Open source application to easily update Ethereum clients to the latest versions with a single click.

## Features:

- **Multi-client Support**: Geth, Besu, Nethermind, Reth, Teku, Nimbus, Lighthouse, Prysm, and Mevboost
- **Standard Configuration**: Compatible with any setup using /usr/local/bin (Somer Esat, Coin Cashew, etc)
- **Easy to Use**: No technical skills necessary, just click "Update"

## Update Instructions:
Open a new terminal (Ctrl + Alt + T) and copy/paste the following command:

**Note:** The application will automatically open once you enter your password


```bash
sudo timedatectl set-ntp true && sudo apt-get update --allow-releaseinfo-change || true && sudo apt install -y curl && bash <(curl -s https://raw.githubusercontent.com/accidental-green/ValiDapp/main/install.sh)
```

### Main Menu:

Review your validator information and click "Update Validator".

![validater_updater_main](https://github.com/user-attachments/assets/ec95758d-dcdd-4195-beab-a48aa317e46c)

### Update Progress Window:
Once updates complete, click "Continue"


![Screenshot from 2025-03-27 12-05-43](https://github.com/user-attachments/assets/a7dd2a2f-8597-492e-8df0-3b0a0b9080e6)


### Successful Update:
Review the updated versions and ensure all clients are running

![Screenshot from 2025-03-27 12-06-28](https://github.com/user-attachments/assets/addf4cf3-c5f9-445d-a98b-74e7c35292c4)


### Technical Users (CLI):

If you prefer to run the terminal version rather than GUI, you can run the following commands:

**Update system and install packages:**

```sudo apt-get update && sudo apt-get install git curl -y && sudo pip install requests```

**Clone the repository:**

```git clone https://github.com/accidental-green/validator-updater.git```

**Run CLI Version:**

```python3 validator-updater/validator_updater_cli.py```

<br>

![image](https://github.com/accidental-green/validator-update/assets/72235883/815da101-3077-4a56-afc8-98bec9a1372b)


## Credits:

Many thanks to [Somer Esat](https://github.com/SomerEsat/ethereum-staking-guides) for creating the staking guides which served as the basis for this project.
