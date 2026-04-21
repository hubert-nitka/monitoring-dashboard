"""
Module contains function to poll information from network devices using netmiko
"""

import time
import json
from typing import Any
from netmiko import ConnectHandler
from netmiko.exceptions import NetMikoAuthenticationException, NetmikoTimeoutException
from config import CISCO_LOGIN, CISCO_PASSWORD, UBUNTU_SERVER_LOGIN, UBUNTU_SERVER_PASSWORD

def get_interfaces_details(devices: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Get interface details from devices
    """
    if isinstance(devices, dict):
        devices = [devices]

    results = []

    for device in devices:

        retries = 3
        delay = 2

        for attempt in range(1, retries + 1):
            connection = None

            try:
                if device['device_vendor'] == 'cisco':
                    connection = ConnectHandler(
                        device_type='cisco_ios',
                        host=device['ip_address'],
                        username=CISCO_LOGIN,
                        password=CISCO_PASSWORD
                    )

                    output = connection.send_command('show interfaces', use_textfsm=True)

                    results.append({
                        'hostname': device['hostname'],
                        'device_id': device['id'],
                        'device_vendor': device['device_vendor'],
                        'interfaces': output
                    })

                    break

                if device['device_vendor'] == 'linux':
                    connection = ConnectHandler(
                        device_type='linux',
                        host=device['ip_address'],
                        username=UBUNTU_SERVER_LOGIN,
                        password=UBUNTU_SERVER_PASSWORD
                    )

                    interfaces_details = json.loads(connection.send_command('ip -j a'))
                    interfaces_counters = json.loads(connection.send_command('ip -s -d -j link'))

                    counters_map = {interface["ifname"]: interface for interface in interfaces_counters}

                    merged = []

                    for interface in interfaces_details:
                        name = interface["ifname"]

                        combined = interface.copy()
                        if name in counters_map:
                            combined.update(counters_map[name])

                        merged.append(combined)

                    results.append({
                        'hostname': device['hostname'],
                        'device_id': device['id'],
                        'device_vendor': device['device_vendor'],
                        'interfaces': merged
                    })

                    break

            except NetmikoTimeoutException:
                print(f"[{device['hostname']}] Timeout (attempt {attempt}/{retries})")

                if attempt == retries:
                    print(f"[{device['hostname']}] FAILED after {retries} retries")
                else:
                    time.sleep(delay)

            except NetMikoAuthenticationException:
                print(f"[{device['hostname']}] Auth failed - skipped")
                break

            finally:
                if connection:
                    connection.disconnect()

    return results

def get_device_facts(devices: dict[str, Any] | list[dict, Any]) -> list[dict[str, Any]]:
    """
    Get base information from devices
    """
    if isinstance(devices, dict):
        devices = [devices]

    results = []

    for device in devices:

        retries = 3
        delay = 2

        for attempt in range(1, retries + 1):
            connection = None

            try:
                if device['device_vendor'] == 'cisco':
                    connection = ConnectHandler(
                        device_type='cisco_ios',
                        host=device['ip_address'],
                        username=CISCO_LOGIN,
                        password=CISCO_PASSWORD
                    )

                    output = connection.send_command('show version', use_textfsm=True)

                    results.append({
                        'hostname': device['hostname'],
                        'device_id': device['id'],
                        'device_vendor': device['device_vendor'],
                        'facts': output
                    })

                    break

                if device['device_vendor'] == 'linux':
                    connection = ConnectHandler(
                        device_type='linux',
                        host=device['ip_address'],
                        username=UBUNTU_SERVER_LOGIN,
                        password=UBUNTU_SERVER_PASSWORD
                    )

                    output = json.loads(connection.send_command('hostnamectl --json=short'))

                    results.append({
                        'hostname': device['hostname'],
                        'device_id': device['id'],
                        'device_vendor': device['device_vendor'],
                        'facts': output
                    })

                    break

            except NetmikoTimeoutException:
                print(f"[{device['hostname']}] Timeout (attempt {attempt}/{retries})")

                if attempt == retries:
                    print(f"[{device['hostname']}] FAILED after {retries} retries")
                else:
                    time.sleep(delay)

            except NetMikoAuthenticationException:
                print(f"[{device['hostname']}] Auth failed - skipped")
                break

            finally:
                if connection:
                    connection.disconnect()

    return results

def get_cdp_neighbors(devices: dict[str, Any] | list[dict, Any]) -> list[dict[str, Any]]:
    """
    Get cdp neighbor details from Cisco devices
    """
    if isinstance(devices, dict):
        devices = [devices]

    results = []

    for device in devices:
        if device['device_vendor'] != 'cisco':
            continue

        retries = 3
        delay = 2

        for attempt in range(1, retries + 1):
            connection = None

            try:

                connection = ConnectHandler(
                    device_type='cisco_ios',
                    host=device['ip_address'],
                    username=CISCO_LOGIN,
                    password=CISCO_PASSWORD
                )

                output = connection.send_command('show cdp neighbors detail', use_textfsm=True)

                results.append({
                    'hostname': device['hostname'],
                    'device_id': device['id'],
                    'device_vendor': device['device_vendor'],
                    'output': output
                })

                break

            except NetmikoTimeoutException:
                print(f"[{device['hostname']}] Timeout (attempt {attempt}/{retries})")

                if attempt == retries:
                    print(f"[{device['hostname']}] FAILED after {retries} retries")
                else:
                    time.sleep(delay)

            except NetMikoAuthenticationException:
                print(f"[{device['hostname']}] Auth failed - skipped")
                break

            finally:
                if connection:
                    connection.disconnect()

    return results
