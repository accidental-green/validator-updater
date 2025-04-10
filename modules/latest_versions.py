import requests
import json

# LATEST VERSIONS ON GITHUB
def check_latest_versions():
    latest_versions = []
    urls = {
        "Geth": "https://api.github.com/repos/ethereum/go-ethereum/releases/latest",
        "Besu": "https://api.github.com/repos/hyperledger/besu/releases/latest",
        "Nethermind": 'https://api.github.com/repos/NethermindEth/nethermind/releases/latest',
        "Reth": 'https://api.github.com/repos/paradigmxyz/reth/releases/latest',
        "Teku": 'https://api.github.com/repos/ConsenSys/teku/releases/latest',
        "Prysm": "https://api.github.com/repos/prysmaticlabs/prysm/releases/latest",
        "Nimbus": 'https://api.github.com/repos/status-im/nimbus-eth2/releases/latest',
        "Lighthouse": 'https://api.github.com/repos/sigp/lighthouse/releases/latest',
        "Mevboost": 'https://api.github.com/repos/flashbots/mev-boost/releases/latest'
    }

    for client, url in urls.items():
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()  # Raises HTTPError for bad HTTP codes
            data = response.json()
            version = data.get('tag_name', 'Unavailable')

            # Prepend 'v' if needed
            if not version.startswith('v') and version != 'Unavailable':
                version = 'v' + version

        except requests.RequestException as e:
            version = 'Unavailable'
            print(f"Error fetching version for {client}: {e}")

        latest_versions.append({client: version})

    print(f'JSON_LATEST: {json.dumps(latest_versions)}')

# Ensure this function is called when the script is executed directly
if __name__ == "__main__":
    check_latest_versions()
