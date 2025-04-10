import subprocess
import sys

def validate_service_name(service_name, valid_services):
    if service_name.lower() in ["none", "empty"]:
        return False
    if service_name.lower() not in valid_services:
        print(f"Invalid service name provided: {service_name}")
        return False
    return True


def start_service(service_name):
    if service_name.lower() in ["none", "empty"]:
        return  # silently skip

    if validate_service_name(service_name, {
        'geth', 'nethermind', 'besu', 'reth', 'teku', 'lighthousebeacon',
        'lighthousevalidator', 'prysmbeacon', 'prysmvalidator', 'nimbus', 'mevboost'
    }):
        try:
            subprocess.run(['sudo', 'systemctl', 'start', service_name], check=True)
            print(f"Successfully started {service_name}")
        except subprocess.CalledProcessError:
            print(f"Warning: Failed to start {service_name}, skipping...")


def start_services(execution_client, consensus_client, validator_client, mevboost_on_off):
    # Normalize names for Lighthouse and Prysm services
    if consensus_client.lower() == "lighthouse":
        consensus_service_name = 'lighthousebeacon'
        validator_service_name = 'lighthousevalidator'
    elif consensus_client.lower() == "prysm":
        consensus_service_name = 'prysmbeacon'
        validator_service_name = 'prysmvalidator'
    else:
        consensus_service_name = consensus_client.lower()
        validator_service_name = validator_client.lower()

    # Start execution client service
    if execution_client.lower() != "none":
        start_service(execution_client.lower())

    # Start consensus client service
    if consensus_service_name != "none":
        start_service(consensus_service_name)

    # Start validator client service
    if validator_service_name != "none" and validator_service_name != consensus_service_name:
        start_service(validator_service_name)

    # Start MEV-Boost if requested
    if mevboost_on_off.lower() == "on":
        start_service('mevboost')

def main():
    if len(sys.argv) != 5:
        print("Usage: python start.py <execution_client> <consensus_client> <validator_client> <mevboost_on_off>")
        sys.exit(1)

    execution_client = sys.argv[1]
    consensus_client = sys.argv[2]
    validator_client = sys.argv[3]
    mevboost_on_off = sys.argv[4]

    start_services(execution_client, consensus_client, validator_client, mevboost_on_off)

if __name__ == "__main__":
    main()
