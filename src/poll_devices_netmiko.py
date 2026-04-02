"""
Module contains function to poll information from network devices using netmiko
"""

from netmiko import ConnectHandler
from typing import Any, overload
from config import CISCO_LOGIN, CISCO_PASSWORD

def get_interfaces_status(devices: dict[str, Any] | list[dict[str, Any]]):
    if isinstance(devices, dict):
        devices = [devices]

    results = []

    for device in devices:
        if device['device_vendor'] == 'cisco':
            connection = ConnectHandler(
                device_type='cisco_ios',
                host=device['ip_address'],
                username=CISCO_LOGIN,
                password=CISCO_PASSWORD
            )  

            output = connection.send_command('show ip interface brief')

            results.append({
                'hostname': device['hostname'],
                
                })
