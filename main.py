import streamlit as st
from src.get_from_db import get_device_by_ip, get_devices_by_vendor, get_inventory_from_db_to_yaml
from src.poll_devices_netmiko import get_interfaces_details, get_device_facts, get_cdp_neighbors
from src.update_db import update_device_status, update_interfaces, save_snapshot
from pprint import pprint
import os
from config import INVENTORY_PATH
import yaml


def main():
    """network_summary = st.Page("pages/network_summary.py", title="👩‍💻 Network Summary", default=True)

    pg = st.navigation([network_summary])
    pg.run()"""

    """devices = get_devices_by_vendor('cisco')
    device = get_device_by_ip('192.168.68.1')
    facts = get_device_facts(device)
    interfaces = get_interfaces_details(device)
    pprint(interfaces)
    for device in interfaces:
        update_interfaces(device['device_id'], device['device_vendor'], device['interfaces'])"""

    """devices = get_inventory_from_db_to_yaml()
    print(devices)
    print(os.getcwd())"""

    with INVENTORY_PATH.open("r") as f:
        inventory = yaml.load(f, Loader=yaml.FullLoader)

    print(inventory)

if __name__ == "__main__":
    main()