"""
Functions for updating DB with current information
"""

from typing import Any
from sqlalchemy import text
from src.utils import connect_to_database, to_int

#######################
### HELPER FUNCTIONS###
#######################

def get_or_create_interface(engine, device_id: int, interface: str) -> int:
    """
    Get interface id from DB or create new one if it does not exist, then return it's ID
    """

    try:
        with engine.begin() as conn:
            result = conn.execute(
                text(
                    """
                    SELECT id FROM interfaces
                    WHERE device_id = :device_id AND name = :interface
                    """
                ),{
                    'device_id': device_id,
                    'interface': interface
                }
            )

            existing_id = result.scalar()

            if existing_id:
                return existing_id

            result = conn.execute(
                text(
                    """
                    INSERT INTO interfaces (device_id, name, oper_status)
                    VALUES (:device_id, :name, :status)
                    RETURNING id
                    """
                ),{
                    'device_id': device_id,
                    'name': interface,
                    'status': None
                }
            )

            return result.scalar()

    except Exception as e:
        raise RuntimeError("Database error while fetching interface id") from e

def get_interface_status(interface_id: int) -> str:
    """
    Get last interface status from DB
    """

    engine = connect_to_database()

    try:
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    """
                    SELECT oper_status
                    FROM interfaces
                    WHERE id = :interface_id
                    """
                ),{
                    'interface_id': interface_id
                }
            )
            return result.scalar()
    except Exception as e:
        raise RuntimeError("Database error while fetching interface status") from e
    finally:
        engine.dispose()

#####################
### MID FUNCTIONS ###
#####################

def save_interface_history(interface_id: int, old_status: str, new_status: str):
    """
    Save interface history to DB
    """

    engine = connect_to_database()

    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO interface_history (interface_id, timestamp, old_status, new_status)
                    VALUES (:interface_id, current_timestamp, :old_status, :new_status)
                    """
                ),{
                    'interface_id': interface_id,
                    'old_status': old_status,
                    'new_status': new_status
                }
            )
    except Exception as e:
        raise RuntimeError("Database error while savind interface history") from e
    finally:
        engine.dispose()

######################
### MAIN FUNCTIONS ###
######################

def update_device_status(device_id: int, status: str):
    """
    Update device status in DB
    """
    engine = connect_to_database()

    try:
        with engine.begin() as conn:
                conn.execute(
                    text(
                        """
                        UPDATE devices
                        SET status = :status
                            last_seen = CASE WHEN :status = 'online' THEN current_timestamp ELSE last_seen END
                        WHERE id = :device_id;
                        """
                    ),{
                        'status': status,
                        'device_id': device_id
                    }
                )
    except Exception as e:
        raise RuntimeError("Database error while updating device status") from e
    finally:
        engine.dispose()

def update_interfaces(device_id: int, device_vendor: str, interfaces: dict[str, Any]):
    """
    Update interface information per device in DB
    """

    engine = connect_to_database()

    try:
        for interface in interfaces:
            with engine.begin() as conn:
                if device_vendor.lower() == 'cisco':
                    interface_id = get_or_create_interface(engine, device_id, interface['interface'])
                    old_status = get_interface_status(interface_id)
                    conn.execute(
                        text(
                            """
                            UPDATE interfaces
                            SET ip_address = :ip_address, description = :description, admin_status = :admin_status,
                            oper_status = :oper_status, in_pkt = :in_pkt, out_pkt = :out_pkt, in_errors = :in_errors,
                            out_errors = :out_errors, out_drops = :out_drops, last_updated = current_timestamp
                            WHERE id = :interface_id
                            """
                        ),{
                            'ip_address': interface['ip_address'] or None,
                            'description': interface['description'],
                            'admin_status': interface['link_status'],
                            'oper_status': interface['protocol_status'],
                            'in_pkt': to_int(interface['input_packets']),
                            'out_pkt': to_int(interface['output_packets']),
                            'in_errors': to_int(interface['input_errors']),
                            'out_errors': to_int(interface['output_errors']),
                            'out_drops': to_int(interface['queue_output_drops']),
                            'interface_id': interface_id
                        }
                    )
                    if old_status != interface['protocol_status']:
                        save_interface_history(interface_id, old_status, interface['protocol_status'])
                if device_vendor.lower() == 'linux':
                    interface_id = get_or_create_interface(engine, device_id, interface['ifname'])
                    old_status = get_interface_status(interface_id)
                    ip_address = next(
                        (
                            addr["local"]
                            for addr in interface.get("addr_info", [])
                            if addr.get("family") == "inet" and addr.get("scope") != "host"
                        ),
                        None
                    )
                    admin_status = "UP" in interface.get("flags", [])
                    stats = interface.get("stats64", {})
                    rx = stats.get("rx", {})
                    tx = stats.get("tx", {})
                    conn.execute(
                        text(
                            """
                            UPDATE interfaces
                            SET ip_address = :ip_address, admin_status = :admin_status,
                            oper_status = :oper_status, in_pkt = :in_pkt, out_pkt = :out_pkt, in_errors = :in_errors,
                            out_errors = :out_errors, out_drops = :out_drops, last_updated = current_timestamp
                            WHERE id = :interface_id
                            """
                        ),{
                            'ip_address': ip_address or None,
                            'admin_status': admin_status,
                            'oper_status': interface['operstate'],
                            'in_pkt': to_int(rx['packets']),
                            'out_pkt': to_int(tx['packets']),
                            'in_errors': to_int(rx['errors']),
                            'out_errors': to_int(tx['errors']),
                            'out_drops': to_int(tx['dropped']),
                            'interface_id': interface_id
                        }
                    )
                    if old_status != interface['operstate']:
                        save_interface_history(interface_id, old_status, interface['operstate'])
    except Exception as e:
        raise RuntimeError("Database error while updating interfaces") from e
    finally:
        engine.dispose()

def save_snapshot(device_id: int, status: str, software: str):
    """
    Save device snapshot to DB
    """

    engine = connect_to_database()

    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO device_snapshots (device_id, timestamp, software_version, status)
                    VALUES (:device_id, current_timestamp, :software_version, :status)
                    """
                ),{
                    'device_id': device_id,
                    'software_version': software,
                    'status': status
                }
            )
    except Exception as e:
        raise RuntimeError("Database error while savind device snapshot") from e
    finally:
        engine.dispose()


