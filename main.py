from src.get_from_db import get_device_by_ip, get_devices_by_vendor
from src.poll_devices_netmiko import get_interfaces_status

def main():
    devices = get_devices_by_vendor('cisco')
    get_interfaces_status(devices)


if __name__ == "__main__":
    main()