# Ethereum Validator Updater

Open source application to easily update Ethereum clients with a single click.

![validater_updater_main](https://github.com/user-attachments/assets/ec95758d-dcdd-4195-beab-a48aa317e46c)

## Features:

- **Multi-client Support**: Geth, Besu, Nethermind, Reth, Teku, Nimbus, Lighthouse, Prysm, and Mevboost
- **Standard Configuration**: Compatible with any setup using /usr/local/bin (Somer Esat, Coin Cashew, etc)
- **Easy to Use**: Built for Home Stakers, no technical skills necessary

## Update Instructions:
Open a new terminal (Ctrl + Alt + T) and copy/paste the following command:

```bash
sudo timedatectl set-ntp true && sudo apt-get update --allow-releaseinfo-change || true && sudo apt install -y curl && bash <(curl -s https://raw.githubusercontent.com/accidental-green/validator-updater/main/install.sh)
```
**Note:** Enter password if prompted, then the application will open automatically


### Main Menu:

Review your validator information and click "Update Validator".

![validater_updater_main](https://github.com/user-attachments/assets/ec95758d-dcdd-4195-beab-a48aa317e46c)

### Update Progress Window:
Wait for updates to complete, then click "Continue"


![Screenshot from 2025-03-27 12-05-43](https://github.com/user-attachments/assets/a7dd2a2f-8597-492e-8df0-3b0a0b9080e6)


### Successfully Updated:
Review the information, then click **Done** to exit or **View Logs** to review client logs

![Screenshot from 2025-03-27 12-06-28](https://github.com/user-attachments/assets/addf4cf3-c5f9-445d-a98b-74e7c35292c4)


### Technical Users (CLI):

If you prefer to run the terminal version rather than GUI, you can run the following commands:

**Update system and install packages:**

```sudo apt-get update && sudo apt-get install git curl -y && sudo pip install requests```

### Download and Run CLI Updater:

```bash
curl -O https://raw.githubusercontent.com/accidental-green/validator-updater/main/modules/validator_updater_cli.py && python3 validator_updater_cli.py
```

### Updater CLI Window:

![image](https://github.com/accidental-green/validator-update/assets/72235883/815da101-3077-4a56-afc8-98bec9a1372b)


## Credits:

Many thanks to [Somer Esat](https://github.com/SomerEsat/ethereum-staking-guides) for creating the staking guides which served as the basis for this project.
