"""
Module contains function to poll information from network devices using napalm
"""
from napalm import get_network_driver
from typing import Any
from config import CISCO_LOGIN, CISCO_PASSWORD, JUNOS_LOGIN, JUNOS_PASSWORD

def get_interfaces_details(devices: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Get interface details from devices
    """

    if isinstance(devices, dict):
        devices = [devices]

    results = []

    for device in devices:

        try:
            if device['device_vendor'] == 'cisco':
                driver = get_network_driver('ios')
                connection = driver(
                    hostname=device['ip_address'],
                    username=CISCO_LOGIN,
                    password=CISCO_PASSWORD
                )
            if device['device_vendor'] == 'juniper':
                driver = get_network_driver('junos')
                connection = driver(
                    hostname=device['ip_address'],
                    username=JUNOS_LOGIN,
                    password=JUNOS_PASSWORD
                )
            connection.open()
            output = connection.get_interfaces()
            results.append({
                'hostname': device['hostname'],
                'device_id': device['id'],
                'device_vendor': device['device_vendor'],
                'interfaces': output
            })
        except Exception as e:
            raise RuntimeError("Error while fetching interfaces details from devices") from e
        finally:
            connection.close()

    return results