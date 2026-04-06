import streamlit as st
from src.get_from_db import get_device_by_ip, get_devices_by_vendor
from src.poll_devices_netmiko import get_interfaces_details, get_device_facts, get_cdp_neighbors
from pprint import pprint

def main():
    """network_summary = st.Page("pages/network_summary.py", title="👩‍💻 Network Summary", default=True)
    
    pg = st.navigation([network_summary])
    pg.run()"""

    devices = get_devices_by_vendor('cisco')
    device = get_device_by_ip('192.168.68.1')
    output = get_device_facts(device)
    pprint(output)


if __name__ == "__main__":
    main()