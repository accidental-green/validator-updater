import os
import requests
import re
import json
import tarfile
import shutil
import subprocess
import tempfile
import urllib.request
import zipfile
import tkinter as tk
import pwd
from tkinter import font
from html.parser import HTMLParser

# Change to the home folder
os.chdir(os.path.expanduser("~"))

# Check sudo privileges
print("Checking sudo privileges")
try:
    subprocess.run(['sudo', '-v'], check=True)
    print("Sudo credentials authenticated.")
except subprocess.CalledProcessError:
    print("Failed to verify sudo credentials.")
    exit(1)


# Define the groups of clients
ec_group = ("geth", "besu", "nethermind")
cc_group = ("teku", "nimbus", "prysm", "lighthouse")

# Define the groups of clients - capitalized
ec_cap = ("Geth", "Besu", "Nethermind")
cc_cap = ("Teku", "Nimbus", "Prysm", "Lighthouse")

# Check if a user exists
def user_exists(username):
    try:
        pwd.getpwnam(username)
        return True
    except KeyError:
        return False

# Define a variable to store data
saved_data = []

def submit():
    execution_client_update = execution_update_var.get()
    consensus_client_update = consensus_update_var.get()
    mevboost_update = mevboost_update_var.get()
    saved_data.extend([execution_client_update, consensus_client_update, mevboost_update])
    root.destroy()
    return execution_client_update, consensus_client_update, mevboost_update

# Initialize the main window
root = tk.Tk()
root.title("Validator Updater")
root.configure(background="#282C34")

# StringVars
execution_update_var = tk.StringVar()
consensus_update_var = tk.StringVar()
mevboost_update_var = tk.StringVar()

# Set default values based on user existence
def set_default_values():
    # Check and set default for execution client
    for client in ec_group:
        if user_exists(client):
            execution_update_var.set(client.capitalize())
            break

    # Check and set default for consensus client
    for client in cc_group:
        username_to_check = client
        if client == "prysm":
            username_to_check = "prysmbeacon"
        elif client == "lighthouse":
            username_to_check = "lighthousebeacon"

        if user_exists(username_to_check):
            consensus_update_var.set(client.capitalize())
            break

    # Check and set default for MEV-Boost
    if user_exists('mevboost'):
        mevboost_update_var.set('Yes')

# Set default values
set_default_values()

# Font
label_font = font.nametofont("TkDefaultFont").copy()
label_font.config(size=20)

# Execution client update selection
execution_update_label = tk.Label(root, text="Execution Client to update:", bg="#282C34", fg="#ABB2BF", font=label_font, anchor='e')
execution_update_label.grid(column=0, row=0, padx=30, pady=30, sticky='e')
execution_clients = ('Nethermind', 'Besu', 'Geth', 'None')
execution_update_menu = tk.OptionMenu(root, execution_update_var, *execution_clients)
execution_update_menu.config(bg="#2196F3", fg="#FFFFFF", activebackground="#64B5F6", activeforeground="#FFFFFF", font=label_font, takefocus=True)
execution_update_menu["menu"].config(bg="#2196F3", fg="#FFFFFF", activebackground="#64B5F6", activeforeground="#FFFFFF", font=label_font)
execution_update_menu.grid(column=1, row=0, padx=30, pady=30, ipadx=40, ipady=10)

# Consensus client update selection
consensus_update_label = tk.Label(root, text="Consensus Client to update:", bg="#282C34", fg="#ABB2BF", font=label_font, anchor='e')
consensus_update_label.grid(column=0, row=1, padx=30, pady=30, sticky='e')
consensus_clients = ('Teku', 'Nimbus', 'Prysm', 'Lighthouse', 'None')
consensus_update_menu = tk.OptionMenu(root, consensus_update_var, *consensus_clients)
consensus_update_menu.config(bg="#FF9800", fg="#FFFFFF", activebackground="#FFA726", activeforeground="#FFFFFF", font=label_font, takefocus=True)
consensus_update_menu["menu"].config(bg="#FF9800", fg="#FFFFFF", activebackground="#FFA726", activeforeground="#FFFFFF", font=label_font)
consensus_update_menu.grid(column=1, row=1, padx=30, pady=30, ipadx=40, ipady=10)

# MEV-Boost update selection
mevboost_update_label = tk.Label(root, text="Update MEV-Boost?", bg="#282C34", fg="#ABB2BF", font=label_font, anchor='e')
mevboost_update_label.grid(column=0, row=2, padx=30, pady=30, sticky='e')
mevboost_options = ('Yes', 'No')
mevboost_update_menu = tk.OptionMenu(root, mevboost_update_var, *mevboost_options)
mevboost_update_menu.config(bg="#4CAF50", fg="#FFFFFF", activebackground="#8BC34A", activeforeground="#FFFFFF", font=label_font, takefocus=True)
mevboost_update_menu["menu"].config(bg="#4CAF50", fg="#FFFFFF", activebackground="#8BC34A", activeforeground="#FFFFFF", font=label_font)
mevboost_update_menu.grid(column=1, row=2, padx=30, pady=30, ipadx=40, ipady=10)

# Update button
update_button = tk.Button(root, text="Update", command=submit, bg="#282C34", fg="#ABB2BF", activebackground="#61AFEF", activeforeground="#282C34", font=label_font, takefocus=True)
update_button.grid(column=1, row=3, padx=30, pady=60)

root.mainloop()

# Retrieve User Input Variables
execution_client_update, consensus_client_update, mevboost_update = saved_data

# Print User Input Variables
print("\n##### User Selected Inputs #####")
print(f"Execution Client to UPDATE: {execution_client_update}")
print(f"Consensus Client to UPDATE: {consensus_client_update}")
print(f"Update MEV-Boost: {mevboost_update}\n")

mevboost_update = mevboost_update.lower()
execution_client_update = execution_client_update.lower()
consensus_client_update = consensus_client_update.lower()

execution_client = execution_client_update
consensus_client = consensus_client_update

########### STOP SERVICES ###############
print("\n########### STOPPING SERVICES ###############\n")
# Stop services based on user input
if execution_client_update == "geth":
    print("Stopping geth service")
    subprocess.run(['sudo', 'systemctl', 'stop', 'geth'])

if execution_client_update == "besu":
    print("Stopping besu service")
    subprocess.run(['sudo', 'systemctl', 'stop', 'besu'])

if execution_client_update == "nethermind":
    print("Stopping nethermind service")
    subprocess.run(['sudo', 'systemctl', 'stop', 'nethermind'])

if consensus_client_update == "teku":
    print("Stopping teku service")
    subprocess.run(['sudo', 'systemctl', 'stop', 'teku'])

if consensus_client_update == "nimbus":
    print("Stopping nimbus service")
    subprocess.run(['sudo', 'systemctl', 'stop', 'nimbus'])

if consensus_client_update == "lighthouse":
    print("Stopping lighthouse beacon service")
    subprocess.run(['sudo', 'systemctl', 'stop', 'lighthousebeacon'])
    print("Stopping lighthouse validator service")
    subprocess.run(['sudo', 'systemctl', 'stop', 'lighthousevalidator'])

if consensus_client_update == "prysm":
    print("Stopping prysm beacon service")
    subprocess.run(['sudo', 'systemctl', 'stop', 'prysmbeacon'])
    print("Stopping prysm validator service")
    subprocess.run(['sudo', 'systemctl', 'stop', 'prysmvalidator'])

# Check if mevboost_update is "mevboost" and stop mevboost service
if mevboost_update == "yes":
    print("Stopping mevboost service")
    subprocess.run(['sudo', 'systemctl', 'stop', 'mevboost'])

class GoReleaseLinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.linux_links = []
        self.capture = False

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr in attrs:
                if attr[0] == 'href' and 'linux-amd64' in attr[1]:
                    self.linux_links.append(attr[1])
                    break

def get_latest_go_linux_release():
    """Fetch the latest Go release URL for Linux."""
    try:
        response = requests.get("https://go.dev/dl/")
        response.raise_for_status()
        parser = GoReleaseLinkParser()
        parser.feed(response.text)
        
        if parser.linux_links:
            return "https://go.dev" + parser.linux_links[0]
        raise Exception("No 64-bit Linux release found")
    except requests.RequestException as e:
        raise Exception("Failed to load the Go downloads page") from e

def append_to_bashrc(content):
    """Append content to .bashrc and update PATH."""
    bashrc_path = os.path.expanduser("~/.bashrc")
    with open(bashrc_path, 'a') as bashrc:
        bashrc.write(content + '\n')
    os.environ["PATH"] += os.pathsep + "/usr/local/go/bin"

def install_go(go_url):
    """Install Go."""
    subprocess.run(["sudo", "apt", "-y", "install", "build-essential"], check=True)
    subprocess.run(["wget", "-O", "go.tar.gz", go_url], check=True)
    subprocess.run(["sudo", "rm", "-rf", "/usr/local/go"], check=True)
    subprocess.run(["sudo", "tar", "-C", "/usr/local", "-xzf", "go.tar.gz"], check=True)
    os.remove("go.tar.gz")
    append_to_bashrc('export PATH=$PATH:/usr/local/go/bin')

def install_mev_boost():
    """Install MEV-Boost and configure its service."""
    
    # Check if 'mevboost' user already exists
    if not user_exists('mevboost'):
        # Create 'mevboost' user if it doesn't exist
        subprocess.run(["sudo", "useradd", "--no-create-home", "--shell", "/bin/false", "mevboost"], check=True)

    # Proceed with MEV-Boost installation
    subprocess.run(['CGO_CFLAGS="-O -D__BLST_PORTABLE__" go install github.com/flashbots/mev-boost@latest'], shell=True)
    mev_boost_path = os.path.join(os.path.expanduser("~"), "go/bin/mev-boost")
    subprocess.run(["sudo", "cp", mev_boost_path, "/usr/local/bin"], check=True)
    subprocess.run(["sudo", "chown", "mevboost:mevboost", "/usr/local/bin/mev-boost"], check=True)

# Main execution mev and go
if mevboost_update == "yes":
    try:
        # Install Go
        go_url = get_latest_go_linux_release()
        print("Latest Go 64-bit release for Linux:", go_url)
        install_go(go_url)

        # Install MEV-Boost
        install_mev_boost()

        # Version checks
        print("\n##### Version Check #####\n")
        
        # Checking Go version
        go_version_output = subprocess.check_output(["go", "version"], text=True)
        print(go_version_output.strip())

        # Checking MEV-Boost version
        mev_boost_version_output = subprocess.check_output(["mev-boost", "--version"], text=True)
        print(mev_boost_version_output.strip())

        print("\n### Go and MEV-Boost Installation Complete ###\n")
    except Exception as e:
        print("Error:", e)

# Change to the home folder
os.chdir(os.path.expanduser("~"))

# Update and upgrade packages
subprocess.run(['sudo', 'apt', '-y', 'update'])
subprocess.run(['sudo', 'apt', '-y', 'upgrade'])

############ GETH ##################
if execution_client == 'geth':
    # Define the URL of the Geth download page
    url = 'https://geth.ethereum.org/downloads/'

    # Send a GET request to the download page and retrieve the HTML response
    response = requests.get(url)
    html = response.text

    # Use regex to extract the URL of the latest Geth binary for Linux (amd64)
    match = re.search(r'href="(https://gethstore\.blob\.core\.windows\.net/builds/geth-linux-amd64-[0-9]+\.[0-9]+\.[0-9]+-[0-9a-f]+\.tar\.gz)"', html)
    if match:
        download_url = match.group(1)
        filename = os.path.expanduser('~/geth.tar.gz')
        print(f'Downloading {download_url}...')
        response = requests.get(download_url)
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f'Done! Binary saved to {filename}.')

        # Extract the contents of the tarball to the user's home folder
        with tarfile.open(filename, 'r:gz') as tar:
            dirname = tar.getnames()[0].split('/')[0]
            tar.extractall(os.path.expanduser('~'))

        # Remove the existing geth executable from /usr/local/bin if it exists
        if os.path.exists('/usr/local/bin/geth'):
            subprocess.run(['sudo', 'rm', '/usr/local/bin/geth'])
            print('Existing geth executable removed from /usr/local/bin.')

        # Copy the geth executable to /usr/local/bin
        src = os.path.expanduser(f'~/{dirname}/geth')
        subprocess.run(['sudo', 'cp', src, '/usr/local/bin/'])
        print('Geth executable copied to /usr/local/bin.')

        # Remove the downloaded file and extracted directory
        os.remove(filename)
        shutil.rmtree(os.path.expanduser(f'~/{dirname}'))
        print(f'Removed {filename} and directory {dirname}.')
        print(f'Download URL: {download_url}')
    else:
        print('Error: could not find download URL.')

    geth_version = download_url.split("/")[-2]

############ BESU ##################
if execution_client == 'besu':
	# Install OpenJDK-17-JRE
	subprocess.run(["sudo", "apt", "-y", "install", "openjdk-17-jre"])

	# Install libjemalloc-dev
	subprocess.run(["sudo", "apt", "install", "-y", "libjemalloc-dev"])

	# Get the latest version number
	url = "https://api.github.com/repos/hyperledger/besu/releases/latest"
	response = urllib.request.urlopen(url)
	data = json.loads(response.read().decode("utf-8"))
	latest_version = data['tag_name']

	besu_version = latest_version

	# Download the latest version
	download_url = f"https://hyperledger.jfrog.io/hyperledger/besu-binaries/besu/{latest_version}/besu-{latest_version}.tar.gz"
	urllib.request.urlretrieve(download_url, f"besu-{latest_version}.tar.gz")

	# Extract the tar.gz file
	with tarfile.open(f"besu-{latest_version}.tar.gz", "r:gz") as tar:
	    tar.extractall()

	# Remove the existing besu executable from /usr/local/bin if it exists
	if os.path.exists('/usr/local/bin/besu'):
	    subprocess.run(['sudo', 'rm', '-r', '/usr/local/bin/besu'])
	    print('Existing Besu executable removed from /usr/local/bin.')

	# Copy the extracted besu folder to /usr/local/bin/besu
	subprocess.run(["sudo", "cp", "-a", f"besu-{latest_version}", "/usr/local/bin/besu"], check=True)

	# Remove the downloaded .tar.gz file
	os.remove(f"besu-{latest_version}.tar.gz")

	print(f'\nSuccessfully installed besu-{latest_version}')

############ NETHERMIND ##################
if execution_client == 'nethermind':
    # Create User and directories
    subprocess.run(["sudo", "useradd", "--no-create-home", "--shell", "/bin/false", "nethermind"])
    subprocess.run(["sudo", "mkdir", "-p", "/var/lib/nethermind"])
    subprocess.run(["sudo", "chown", "-R", "nethermind:nethermind", "/var/lib/nethermind"])
    subprocess.run(["sudo", "apt-get", "install", "libsnappy-dev", "libc6-dev", "libc6", "unzip", "-y"], check=True)

    # Define the Github API endpoint to get the latest release
    url = 'https://api.github.com/repos/NethermindEth/nethermind/releases/latest'

    # Send a GET request to the API endpoint
    response = requests.get(url)

    # Search for the asset with the name that ends in linux-x64.zip
    assets = response.json()['assets']
    download_url = None
    zip_filename = None
    for asset in assets:
        if asset['name'].endswith('linux-x64.zip'):
            download_url = asset['browser_download_url']
            zip_filename = asset['name']
            break

    if download_url is None or zip_filename is None:
        print("Error: Could not find the download URL for the latest release.")
        exit(1)

    # Download the latest release binary
    response = requests.get(download_url)

    # Save the binary to a temporary file
    with tempfile.NamedTemporaryFile('wb', suffix='.zip', delete=False) as temp_file:
        temp_file.write(response.content)
        temp_path = temp_file.name

    # Create a temporary directory for extraction
    with tempfile.TemporaryDirectory() as temp_dir:
        # Extract the binary to the temporary directory
        with zipfile.ZipFile(temp_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Copy the contents of the temporary directory to /usr/local/bin/nethermind using sudo
        subprocess.run(["sudo", "cp", "-a", f"{temp_dir}/.", "/usr/local/bin/nethermind"])

    # chown nethermind:nethermind /usr/local/bin/nethermind
    subprocess.run(["sudo", "chown", "nethermind:nethermind", "/usr/local/bin/nethermind"])

    # chown nethermind:nethermind /usr/local/bin/nethermind/nethermind
    subprocess.run(["sudo", "chown", "nethermind:nethermind", "/usr/local/bin/nethermind/nethermind"])

    # chmod a+x /usr/local/bin/nethermind/nethermind
    subprocess.run(["sudo", "chmod", "a+x", "/usr/local/bin/nethermind/nethermind"])

    # Remove the temporary zip file
    os.remove(temp_path)

    nethermind_version = os.path.splitext(zip_filename)[0]

############ TEKU ##################
if consensus_client == 'teku':
    # Change to the home folder
    os.chdir(os.path.expanduser("~"))

    # Define the Github API endpoint to get the latest release
    url = 'https://api.github.com/repos/ConsenSys/teku/releases/latest'

    # Send a GET request to the API endpoint
    response = requests.get(url)

    # Get the latest release tag
    latest_version = response.json()['tag_name']

    # Define the download URL for the latest release
    download_url = f"https://artifacts.consensys.net/public/teku/raw/names/teku.tar.gz/versions/{latest_version}/teku-{latest_version}.tar.gz"
    teku_version = latest_version
    # Download the latest release binary
    response = requests.get(download_url)

    # Save the binary to the home folder
    with open('teku.tar.gz', 'wb') as f:
        f.write(response.content)

    # Extract the binary to the home folder
    with tarfile.open('teku.tar.gz', 'r:gz') as tar:
        tar.extractall()

    # Copy the binary folder to /usr/local/bin using sudo
    os.system(f"sudo cp -r teku-{latest_version} /usr/local/bin/teku")

    # Remove the teku.tar.gz file and extracted binary folder
    os.remove('teku.tar.gz')
    shutil.rmtree(f'teku-{latest_version}')

    print("Teku binary installed successfully!")
    print(f"Download URL: {download_url}")
    print(f"teku-v{latest_version}")

################ PRYSM ###################
if consensus_client == 'prysm':
    base_url = "https://api.github.com/repos/prysmaticlabs/prysm/releases/latest"
    response = requests.get(base_url)
    response_json = response.json()
    download_links = []

    for asset in response_json["assets"]:
        if re.search(r'beacon-chain-v\d+\.\d+\.\d+-linux-amd64$', asset["browser_download_url"]):
            download_links.append(asset["browser_download_url"])
        elif re.search(r'validator-v\d+\.\d+\.\d+-linux-amd64$', asset["browser_download_url"]):
            download_links.append(asset["browser_download_url"])

    if len(download_links) >= 2:
        for link in download_links[:2]:
            cmd = f"curl -LO {link}"
            os.system(cmd)

        os.system("mv beacon-chain-*-linux-amd64 beacon-chain")
        os.system("mv validator-*-linux-amd64 validator")
        os.system("chmod +x beacon-chain")
        os.system("chmod +x validator")
        os.system("sudo cp beacon-chain /usr/local/bin")
        os.system("sudo cp validator /usr/local/bin")
        os.system("rm beacon-chain && rm validator")
    else:
        print("Error: Could not find the latest release links.")

    prysm_version = link.split("/")[-1]

    print(f"Successfully installed Prsym {prysm_version}")

################ NIMBUS ##################
if consensus_client == 'nimbus':
    # Change to the home folder
    os.chdir(os.path.expanduser("~"))

    # Define the Github API endpoint to get the latest release
    url = 'https://api.github.com/repos/status-im/nimbus-eth2/releases/latest'

    # Send a GET request to the API endpoint
    response = requests.get(url)

    # Search for the asset with the name that ends in _Linux_amd64.tar.gz
    assets = response.json()['assets']
    download_url = None
    for asset in assets:
        if '_Linux_amd64' in asset['name'] and asset['name'].endswith('.tar.gz'):
            download_url = asset['browser_download_url']
            break

    if download_url is None:
        print("Error: Could not find the download URL for the latest release.")
        exit(1)

    # Download the latest release binary
    response = requests.get(download_url)

    # Save the binary to the home folder
    with open('nimbus.tar.gz', 'wb') as f:
        f.write(response.content)

    # Extract the binary to the home folder
    with tarfile.open('nimbus.tar.gz', 'r:gz') as tar:
        tar.extractall()

    # Find the extracted folder
    extracted_folder = None
    for item in os.listdir():
        if item.startswith("nimbus-eth2_Linux_amd64"):
            extracted_folder = item
            break

    if extracted_folder is None:
        print("Error: Could not find the extracted folder.")
        exit(1)

    # Copy the binary to /usr/local/bin using sudo
    os.system(f"sudo cp {extracted_folder}/build/nimbus_beacon_node /usr/local/bin")

    # Remove the nimbus.tar.gz file and extracted folder
    os.remove('nimbus.tar.gz')
    os.system(f"rm -r {extracted_folder}")
    
    version = download_url.split("/")[-2]

    print("Nimbus binary installed successfully!")
    print(f"Download URL: {download_url}")
    print(f"\nSuccessfully Installed Nimbus Version {version}")

############ LIGHTHOUSE ##################
if consensus_client == 'lighthouse':
    # Change to the home folder
    os.chdir(os.path.expanduser("~"))

    # Define the Github API endpoint to get the latest release
    url = 'https://api.github.com/repos/sigp/lighthouse/releases/latest'

    # Send a GET request to the API endpoint
    response = requests.get(url)

    # Search for the asset with the name that ends in x86_64-unknown-linux-gnu.tar.gz
    assets = response.json()['assets']
    download_url = None
    for asset in assets:
        if asset['name'].endswith('x86_64-unknown-linux-gnu.tar.gz'):
            download_url = asset['browser_download_url']
            break

    if download_url is None:
        print("Error: Could not find the download URL for the latest release.")
        exit(1)

    # Download the latest release binary
    response = requests.get(download_url)

    # Save the binary to the home folder
    with open('lighthouse.tar.gz', 'wb') as f:
        f.write(response.content)

    # Extract the binary to the home folder
    with tarfile.open('lighthouse.tar.gz', 'r:gz') as tar:
        tar.extractall()

    # Copy the binary to /usr/local/bin using sudo
    os.system("sudo cp lighthouse /usr/local/bin")

    # Remove the lighthouse.tar.gz file and extracted binary
    os.remove('lighthouse.tar.gz')
    os.remove('lighthouse')

    lighthouse_version = download_url.split("/")[-2]

    print("Lighthouse binary installed successfully!")
    print(f"Download URL: {download_url}")

######## PRINT OUTPUT ############
print("\nUpdate Successful! See versions listed below:")
# Geth Print
if execution_client == 'geth':
    geth_version = subprocess.run(["geth", "--version"], stdout=subprocess.PIPE).stdout
    if geth_version is not None:
        geth_version = geth_version.decode()
        geth_version = (geth_version.split(" ")[-1]).split("-")[-3]
    else:
        geth_version = ""
    print(f'\nGeth Version: v{geth_version}\n')

# Besu Print
if execution_client == 'besu':
    print(f'\nBesu Version: v{besu_version}\n')

# Nethermind Print
if execution_client == 'nethermind':
    # Use regular expression to extract the version number
    match = re.search(r'(\d+\.\d+\.\d+)', nethermind_version)
    
    if match:
        extracted_version = match.group(1)
        print(f'\nNethermind Version: v{extracted_version}\n')

# Teku Print
if consensus_client == 'teku':
    print(f"Teku Version: v{latest_version}\n")

# Prysm Print
if consensus_client == 'prysm':
    prysm_version = subprocess.run(["beacon-chain", "--version"], stdout=subprocess.PIPE).stdout
    if prysm_version is not None:
        prysm_version = prysm_version.decode().splitlines()[0]
        prysm_version = prysm_version.split("/")[-2]
    else:
        prysm_version = ""
    print(f'Prysm Version: {prysm_version}\n')

# Nimbus Print
if consensus_client == 'nimbus':
    nimbus_version = subprocess.run(["nimbus_beacon_node", "--version"], stdout=subprocess.PIPE).stdout
    if nimbus_version is not None:
        nimbus_version = nimbus_version.decode().splitlines()[0]
        nimbus_version = nimbus_version.split(" ")[-1]
        nimbus_version = nimbus_version.split("-")[-3]
    else:
        nimbus_version = ""
    print(f'Nimbus Version: {nimbus_version}\n')

# LIGHTHOUSE PRINT
if consensus_client == 'lighthouse':
    lighthouse_version = subprocess.run(["lighthouse", "-V"], stdout=subprocess.PIPE).stdout
    if lighthouse_version is not None:
        lighthouse_version = lighthouse_version.decode()
        lighthouse_version = (lighthouse_version.split(" ")[-1]).split("-")[-2]
    else:
        lighthouse_version = ""
    print(f'Lighthouse Version: {lighthouse_version}\n')

# MEV BOOST PRINT
if mevboost_update == "yes":
    # Check MEV-Boost version
    output = subprocess.check_output(["mev-boost", "-version"], text=True)
    version = output.split()[-1]
    print(f"Mevboost Version: {output.split()[-1]}\n")

print("\n Start service files to begin running the updated clients.\n")

