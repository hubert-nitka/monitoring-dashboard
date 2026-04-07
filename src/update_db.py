"""
Functions for updating DB with current information
"""

from typing import Any
from sqlalchemy import text
from src.utils import connect_to_database

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
                    INSERT INTO interfaces (device_id, name)
                    VALUES (:device_id, :name)
                    RETURNING id
                    """
                ),{
                    'device_id': device_id,
                    'name': interface
                }
            )
            
            return result.scalar()

    except Exception as e:
        raise RuntimeError("Database error while fetching interface id") from e



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
            if status.lower() == "offline":
                conn.execute(
                    text(
                        """
                        UPDATE devices
                        SET status = :status
                        WHERE id = :device_id;
                        """
                    ),{
                        'status': status,
                        'device_id': device_id
                    }
                )
            if status.lower() == "online":
                conn.execute(
                    text(
                        """
                        UPDATE devices
                        SET status = :status, last_seen = current_timestamp
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
            interface_id = get_or_create_interface(engine, device_id, interface['interface'])
            with engine.begin() as conn:
                if device_vendor.lower() == 'cisco':
                    conn.execute(
                        text(
                            """
                            UPDATE interfaces
                            SET ip_address = :ip_address, description = :description, admin_status = :admin_status,
                            oper_status = :oper_status, in_pkt = :in_pkt, out_pkt = :out_pkt, in_errors = :in_errors,
                            out_errors = :out_errors, out_drops = :out_drops, last_updated = current_timestamp
                            """
                        ),{
                            'ip_address': interface['ip_address'],
                            'description': interface['description'],
                            'admin_status': interface['link_status'],
                            'oper_status': interface['protocol_status'],
                            'in_pkt': interface['input_packets'],
                            'out_pkt': interface['output_packets'],
                            'in_errors': interface['input_errors'],
                            'out_errors': interface['output_errors'],
                            'out_drops': interface['queue_output_drops']
                        }
                    )
                if device_vendor.lower() == 'linux': 
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
                            """
                        ),{
                            'ip_address': ip_address,
                            'admin_status': admin_status,
                            'oper_status': interface['operstate'],
                            'in_pkt': rx['packets'],
                            'out_pkt': tx['packets'],
                            'in_errors': rx['errors'],
                            'out_errors': tx['errors'],
                            'out_drops': tx['dropped']
                        }
                    )
    except Exception as e:
        raise RuntimeError("Database error while updating interfaces") from e
    finally:
        engine.dispose()