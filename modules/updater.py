import install
import sys
import stop
import start
import prints

def handle_update(execution, consensus, mevboost):
    print("STARTING UPDATE...")
    print("UPDATE -- BLANK")
    print(f"Execution Client: {execution.upper()}")
    print(f"Consensus Client: {consensus.upper()}")
    print(f"MEVboost: {mevboost.upper()}")
    print("UPDATE -- BLANK")

    # Stop Services
    stop.stop_services(execution, consensus, consensus, mevboost)

    # Stop Services
    print("UPDATE - STEP 1: Stopping Clients")
    print("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Note: All clients will be restarted after updates")


    # Run Updates
    print("UPDATE - STEP 2: Update System")
    print("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Note: System updates may take a while")

    install.run_updates()

    # Update Execution Client if applicable
    if execution.lower() != 'empty':
        print(f"UPDATE - STEP 3: Updating Execution Client ({execution.upper()})")
        install.install_client(execution)
    else:
        print("Skipping execution client update")

    # Update Consensus Client if applicable
    if consensus.lower() != 'empty':
        print(f"UPDATE - STEP 4: Updating Consensus Client ({consensus.upper()})")
        install.install_client(consensus)
    else:
        print("Skipping consensus client update")

    # Install MEV-Boost if applicable
    if mevboost.lower() == "on":
        print("UPDATE - STEP 5: Updating MEVboost")
        install.install_mev()
    else:
        print("Skipping MEVboost update")
    print("UPDATE -- BLANK")

    # Print & Version Check
    prints.print_updater(execution, consensus, mevboost)
    print("UPDATE -- BLANK")

    # Start Services
    start.start_services(execution, consensus, consensus, mevboost)


# Main script entry point
if __name__ == "__main__":
    if len(sys.argv) == 4:
        execution = sys.argv[1].lower()
        consensus = sys.argv[2].lower()
        mevboost = sys.argv[3].lower()
        
        handle_update(execution, consensus, mevboost)
    else:
        print("Please provide all required parameters.")
