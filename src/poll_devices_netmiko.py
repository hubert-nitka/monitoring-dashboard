"""
Module contains function to poll information from network devices using netmiko
"""

from netmiko import ConnectHandler


"""connection = ConnectHandler(
    host = "192.168.69.1",
    username = "cisco",
    password = "cisco",
    device_type = "cisco_ios"
)

output = connection.send_command("sh mac add")

print(output)

connection.disconnect()"""

