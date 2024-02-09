#!/usr/bin/python3

import argparse
import os
from multiprocessing.connection import Client

def main():
    parser = argparse.ArgumentParser(description="Fancytools")

    parser.add_argument('-d', '--diagnostic', nargs='*', dest='diagnostic_args',
                        help='A full anonymized system report will be prompted. Additional arguments are accepted.')
    parser.add_argument('-p', '--plugin', dest='plugin', help='Name of the plugin to toggle')
    parser.add_argument('-e', '--enable', action='store_true', dest='enable',
                        help='Enable the specified plugin (default is to disable)')
    args = parser.parse_args()

    if args.diagnostic_args is not None:
        script_path = os.path.abspath(__file__)

        print(f"The path of the running script is: {script_path}")

        # Get the real file location
        real_path = os.path.realpath(script_path)

        print(f"The real path of the script is: {real_path}")

        # Split the original path into its components
        components = real_path.split(os.path.sep)

        # Modify the components to create the new path
        components[-2:] = ["tools", "default", "dev", "diagnostic.sh"]

        # Join the modified components to form the new path
        new_path = os.path.join(*components)

        print(f"The transformed path is: {new_path}")

        os.system('/' + new_path)

    if args.plugin:
        if args.enable:
            enable_state = 'True'
        else:
            enable_state = 'False'

        status = 0
        address = ('localhost', 3699)
        while True:
            try:
                conn = Client(address)
                conn.send(['plugin', args.plugin, enable_state])
                conn.close()
                print(f'Success {args.plugin}.enable={enable_state}')
                break  # Exit the loop if the connection and data sending are successful

            except ConnectionRefusedError as cre:
                print(f"Connection refused error: {cre}")
                time.sleep(5)  # wait for a few seconds before attempting to reconnect
                continue  # Continue the loop to retry the connection

if __name__ == "__main__":
    main()
