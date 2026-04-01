"""
Functions to get data from DB
"""

from sqlalchemy import text
from src.utils import connect_to_database

########################
### HELPER FUNCTIONS ###
########################



######################
### MAIN FUNCTIONS ###
######################

def get_device_by_ip(ip_address):
    """
    Get device from DB by IP_address
    """

    engine = connect_to_database()
    device = None

    try:
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    """
                    SELECT d.id, d.hostname, d.ip_address, d.serial_number, dt.name AS device_type, v.name AS device_vendor, d.model, d.software_version, d.status, d.priority
                    FROM devices d
                    JOIN device_types dt 
                        ON d.type_id = dt.id
                    JOIN vendors v
                        ON d.vendor_id = v.id
                    WHERE d.ip_address = :ip_address;
                    """
                ),{'ip_address': ip_address}
            )

            device = result.mappings().fetchone()
    except Exception as e:
        raise RuntimeError(f"Database error while fetching device with IP {ip_address}") from e
    finally:
        engine.dispose()
    if device is None:
        raise ValueError(f'Device with IP {ip_address} does not exist in DB')
    return device

def get_devices_by_vendor(vendor):
    """
    Get list of devices from DB by vendor
    """
    
    engine = connect_to_database()
    devices = None

    try:
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    """
                    SELECT d.id, d.hostname, d.ip_address, d.serial_number, dt.name AS device_type, v.name AS device_vendor, d.model, d.software_version, d.status, d.priority
                    FROM devices d
                    JOIN device_types dt 
                        ON d.type_id = dt.id
                    JOIN vendors v
                        ON d.vendor_id = v.id
                    WHERE v.name = :vendor;
                    """
                ),{'vendor': vendor.title()}
            )
            devices = result.mappings().fetchall()
    except Exception as e:
        raise RuntimeError(f"Database error while fetching devices by '{vendor}' vendor") from e
    finally:
        engine.dispose()
    if not devices:
        raise ValueError(f"Devices with '{vendor}' vendor do not exist in DB")
    return devices
