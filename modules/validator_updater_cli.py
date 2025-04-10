import os
import requests
import re
import json
import tarfile
import shutil
import subprocess
import tempfile
import pwd
import urllib.request
import zipfile
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

# Check if a user exists
def user_exists(username):
    try:
        pwd.getpwnam(username)
        return True
    except KeyError:
        return False

# Prompt User to select an Ethereum execution client
def is_valid_client(client):
    valid_exec_clients = ['GETH', 'BESU', 'NETHERMIND', 'RETH', 'SKIP']
    return client in valid_exec_clients

while True:
    execution_client = input("\nSelect Execution Client to update: (geth, besu, nethermind, reth, or skip): ").upper()
    if is_valid_client(execution_client):
        print(f"Selected client: {execution_client}")
        break
    else:
        print("Invalid client. Please try again.")

execution_client = execution_client.lower()
execution_client_cap = execution_client.capitalize()

# Prompt User to select a consensus client
def is_valid_consensus_client(client):
    valid_consensus_clients = ['LIGHTHOUSE', 'TEKU', 'PRYSM', 'NIMBUS', 'SKIP']
    return client in valid_consensus_clients

while True:
    consensus_client = input("\nSelect Consensus Client to update: (lighthouse, teku, prysm, nimbus, or skip): ").upper()
    if is_valid_consensus_client(consensus_client):
        print(f"Selected client: {consensus_client}")
        break
    else:
        print("Invalid client. Please try again.")

consensus_client = consensus_client.lower()
consensus_client_cap = consensus_client.capitalize()

# Prompt User to update MEVBoost
while True:
    mevboost_update = input("\nWould you like to update mevboost? (yes/no): ").strip().lower()
    if mevboost_update in ['yes', 'no']:
        break
    else:
        print("Invalid choice. Please enter 'yes' or 'no'.")

########### STOP SERVICES ###############
print("\n########### STOPPING SERVICES ###############\n")
# Stop services based on user input
if execution_client == "geth":
    print("Stopping geth service")
    subprocess.run(['sudo', 'systemctl', 'stop', 'geth'])

if execution_client == "besu":
    print("Stopping besu service")
    subprocess.run(['sudo', 'systemctl', 'stop', 'besu'])

if execution_client == "nethermind":
    print("Stopping nethermind service")
    subprocess.run(['sudo', 'systemctl', 'stop', 'nethermind'])

if execution_client == "reth":
    print("Stopping reth service")
    subprocess.run(['sudo', 'systemctl', 'stop', 'reth'])

if consensus_client == "teku":
    print("Stopping teku service")
    subprocess.run(['sudo', 'systemctl', 'stop', 'teku'])

if consensus_client == "nimbus":
    print("Stopping nimbus service")
    subprocess.run(['sudo', 'systemctl', 'stop', 'nimbus'])

if consensus_client == "lighthouse":
    print("Stopping lighthouse beacon service")
    subprocess.run(['sudo', 'systemctl', 'stop', 'lighthousebeacon'])
    print("Stopping lighthouse validator service")
    subprocess.run(['sudo', 'systemctl', 'stop', 'lighthousevalidator'])

if consensus_client == "prysm":
    print("Stopping prysm beacon service")
    subprocess.run(['sudo', 'systemctl', 'stop', 'prysmbeacon'])
    print("Stopping prysm validator service")
    subprocess.run(['sudo', 'systemctl', 'stop', 'prysmvalidator'])

if mevboost_update == "yes":
    print("Stopping mevboost service")
    subprocess.run(['sudo', 'systemctl', 'stop', 'mevboost'])

# Update and upgrade packages
subprocess.run(['sudo', 'apt', '-y', 'update'])
subprocess.run(['sudo', 'apt', '-y', 'upgrade'])

###### INSTALL GO AND MEVBOOST #######
if mevboost_update == 'yes':
    print("Installing Go and MEVBoost...")
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

# Variables
mevboost_update = mevboost_update.lower()
execution_client = execution_client.lower()
consensus_client = consensus_client.lower()

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
    # Install dependencies
    subprocess.run(["sudo", "apt", "-y", "install", "openjdk-21-jre"])
    subprocess.run(["sudo", "apt", "install", "-y", "libjemalloc-dev"])

    # Create user and directories
    subprocess.run(['sudo', 'useradd', '--no-create-home', '--shell', '/bin/false', 'besu'])
    subprocess.run(['sudo', 'mkdir', '-p', '/var/lib/besu'])
    subprocess.run(['sudo', 'chown', '-R', 'besu:besu', '/var/lib/besu'])

    # Get latest version info
    url = "https://api.github.com/repos/hyperledger/besu/releases/latest"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read().decode("utf-8"))
    latest_version = data['tag_name']

    # Download and extract
    download_url = f"https://github.com/hyperledger/besu/releases/download/{latest_version}/besu-{latest_version}.tar.gz"
    file_path, _ = urllib.request.urlretrieve(download_url)
    dirname = f"besu-{latest_version}"

    with tarfile.open(file_path, "r:gz") as tar:
        tar.extractall()

    # Remove previous if exists
    if os.path.exists('/usr/local/bin/besu'):
        subprocess.run(['sudo', 'rm', '-r', '/usr/local/bin/besu'])
        print('Existing Besu executable removed from /usr/local/bin.')

    # Move new
    subprocess.run(["sudo", "cp", "-a", dirname, "/usr/local/bin/besu"], check=True)

    # Cleanup
    os.remove(file_path)
    shutil.rmtree(dirname)

    print(f"\nSuccessfully installed Besu {latest_version}")

############ NETHERMIND ##################
if execution_client == 'nethermind':
    try:
        subprocess.run(["sudo", "useradd", "--no-create-home", "--shell", "/bin/false", "nethermind"], check=False)
        subprocess.run(["sudo", "mkdir", "-p", "/var/lib/nethermind"], check=True)
        subprocess.run(["sudo", "chown", "-R", "nethermind:nethermind", "/var/lib/nethermind"], check=True)
        subprocess.run(["sudo", "apt-get", "install", "libsnappy-dev", "libc6-dev", "libc6", "unzip", "-y"], check=True)

        url = 'https://api.github.com/repos/NethermindEth/nethermind/releases/latest'
        response = requests.get(url)
        assets = response.json()['assets']
        download_url = next((a['browser_download_url'] for a in assets if a['name'].endswith('linux-x64.zip')), None)
        zip_filename = download_url.split('/')[-1]

        if not download_url:
            print("Error: Could not find the download URL for the latest release.")
            exit(1)

        temp_path = f"/tmp/{zip_filename}"
        urllib.request.urlretrieve(download_url, temp_path)

        # Clean old install
        subprocess.run(["sudo", "rm", "-rf", "/usr/local/bin/nethermind"], check=True)
        subprocess.run(["sudo", "mkdir", "-p", "/usr/local/bin/nethermind"], check=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(temp_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            subprocess.run(["sudo", "cp", "-a", f"{temp_dir}/.", "/usr/local/bin/nethermind"], check=True)

        # Set executable + owner
        subprocess.run(["sudo", "chmod", "+x", "/usr/local/bin/nethermind/nethermind"], check=True)
        subprocess.run(["sudo", "chown", "-R", "nethermind:nethermind", "/usr/local/bin/nethermind"], check=True)

        # Clean up
        os.remove(temp_path)

        nethermind_version = response.json()['tag_name']
        print(f"\nSuccessfully installed Nethermind {nethermind_version}")

    except Exception as e:
        print(f"Failed to install Nethermind: {e}")

############ RETH INSTALL ##################
if execution_client == 'reth':
    # Create User and directories
    subprocess.run(['sudo', 'useradd', '--no-create-home', '--shell', '/bin/false', 'reth'], stderr=subprocess.DEVNULL)
    subprocess.run(['sudo', 'mkdir', '-p', '/var/lib/reth'], check=True)
    subprocess.run(['sudo', 'chown', '-R', 'reth:reth', '/var/lib/reth'], check=True)

    # Define the Github API endpoint to get the latest release
    url = "https://api.github.com/repos/paradigmxyz/reth/releases/latest"

    # Get the latest release info
    response = requests.get(url)
    reth_version = response.json()['tag_name']

    # Search for the asset with the correct tar.gz format
    assets = response.json()['assets']
    download_url = None
    tar_filename = None
    for asset in assets:
        if asset['name'].endswith('x86_64-unknown-linux-gnu.tar.gz'):
            if asset['name'].startswith('reth'):
                download_url = asset['browser_download_url']
                tar_filename = asset['name']
                break

    if download_url is None or tar_filename is None:
        print("Error: Could not find the download URL for the latest release.")
        exit(1)

    # Download the latest release binary
    urllib.request.urlretrieve(download_url, f"/tmp/{tar_filename}")

    # Create a temporary extraction directory
    temp_extract_dir = "/tmp/reth_extracted"
    subprocess.run(["mkdir", "-p", temp_extract_dir], check=True)

    # Extract the tar.gz file into the temporary directory
    with tarfile.open(f"/tmp/{tar_filename}", "r:gz") as tar:
        tar.extractall(path=temp_extract_dir)

    # Identify the extracted binary (ensure correct name)
    extracted_binary_path = os.path.join(temp_extract_dir, "reth")

    if not os.path.isfile(extracted_binary_path):
        print("Error: Reth binary not found after extraction.")
        exit(1)

    # Move the binary to /usr/local/bin with sudo
    subprocess.run(["sudo", "mv", extracted_binary_path, "/usr/local/bin/reth"], check=True)

    # Set the correct ownership and permissions
    subprocess.run(["sudo", "chown", "reth:reth", "/usr/local/bin/reth"], check=True)
    subprocess.run(["sudo", "chmod", "755", "/usr/local/bin/reth"], check=True)

    # Clean up temporary files
    os.remove(f"/tmp/{tar_filename}")
    subprocess.run(["rm", "-rf", temp_extract_dir], check=True)

    print("Reth installation completed successfully!")

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
print("\n########## UPDATE COMPLETE ##########\n")
# Geth Print
if execution_client == 'geth':
    geth_version = subprocess.run(["geth", "--version"], stdout=subprocess.PIPE).stdout
    if geth_version is not None:
        geth_version = geth_version.decode()
        geth_version = (geth_version.split(" ")[-1]).split("-")[-3]
    else:
        geth_version = ""
    print(f'Geth Version: v{geth_version}\n')

# Besu Print
if execution_client == 'besu':
    besu_output = subprocess.run(["sudo", "/usr/local/bin/besu/bin/besu", "--version"], stdout=subprocess.PIPE, text=True)
    if besu_output.returncode == 0:
        besu_version = besu_output.stdout.strip().split('/')[1].split('/')[0]
    else:
        besu_version = "Failed to execute command"
    print(f'Besu Version: {besu_version}\n')

# Nethermind Print

if execution_client == 'nethermind':
    output = subprocess.check_output(["sudo", "/usr/local/bin/nethermind/nethermind", "--version"], text=True)
    version = output.split("Version:")[-1].split()[0]
    print(f'Nethermind Version: v{version}')

# Reth Print
if execution_client == 'reth':
    result = subprocess.run(["reth", "--version"], stdout=subprocess.PIPE, text=True)
    for line in result.stdout.splitlines():
        if "Version:" in line:
            reth_version = line.split("Version:")[1].strip()
            print(f"Reth Version: v{reth_version}")
            break


# Teku Print
if consensus_client == 'teku':
    teku_output = subprocess.run(["sudo", "/usr/local/bin/teku/bin/teku", "--version"], stdout=subprocess.PIPE, text=True)
    if teku_output.returncode == 0:
        version_line = teku_output.stdout.strip().splitlines()[0]
        version_parts = version_line.split('/')
        if len(version_parts) >= 2:
            teku_version = version_parts[1].split('-')[0]
        else:
            teku_version = "Version information not found"
    else:
        teku_version = "Failed to execute command"
    print(f'Teku Version: {teku_version}\n')

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
    nimbus_output = subprocess.run(["nimbus_beacon_node", "--version"], stdout=subprocess.PIPE, text=True)
    if nimbus_output.returncode == 0:
        version_parts = nimbus_output.stdout.strip().split()[3].split('-')
        nimbus_version = version_parts[0]
    else:
        nimbus_version = "Failed to execute command"
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
    try:
        output = subprocess.check_output(
            ["mev-boost", "--version"],
            stderr=subprocess.STDOUT,
            text=True
        ).strip()

        match = re.search(r'v\d+\.\d+\.\d+', output)
        version = match.group(0) if match else "Unavailable"
        print(f"Mevboost Version: {version}")

    except Exception:
        print("Mevboost Version: Unavailable")

# Constructing the list of services to start
services_to_start = [execution_client.lower(), consensus_client.lower()]
if mevboost_update == "yes":
    services_to_start.append("mevboost".lower())

# Constructing the list of services to start
services_to_start = [execution_client.lower(), consensus_client.lower()]
if mevboost_update == "yes":
    services_to_start.append("mevboost".lower())

# Constructing the services string
if len(services_to_start) == 1:
    services_str = services_to_start[0]
elif len(services_to_start) == 2:
    services_str = " and ".join(services_to_start)
else:
    services_str = ", ".join(services_to_start[:-1]) + ", and " + services_to_start[-1]

# Printing Start Services
print("########## START SERVICES ##########\n")

allowed_responses = ['y', 'n', 'yes', 'no']
response = input(f"Would you like to start {services_str}? (yes/no): ").lower()

while response not in allowed_responses:
    print("Invalid selection. Please try again.")
    response = input(f"Would you like to start {services_str}? (yes/no): ").lower()

if response in ['y', 'yes']:
    if 'prysm' in services_to_start:
        subprocess.run(["sudo", "systemctl", "start", "prysmbeacon"])
        subprocess.run(["sudo", "systemctl", "start", "prysmvalidator"])
        services_to_start.remove('prysm')
    elif 'lighthouse' in services_to_start:
        subprocess.run(["sudo", "systemctl", "start", "lighthousebeacon"])
        subprocess.run(["sudo", "systemctl", "start", "lighthousevalidator"])
        services_to_start.remove('lighthouse')
    
    # Start execution client and MEV service if selected
    for service in services_to_start:
        subprocess.run(["sudo", "systemctl", "start", service])
    
    print("\nStarting services, validators should be online momentarily!\n")
else:
    print("\nUpdate complete! You can start services in order to begin attesting again.\n")
