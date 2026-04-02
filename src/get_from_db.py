"""
Functions to get data from DB
"""

from sqlalchemy import text
from src.utils import connect_to_database
from typing import Any, overload

BASE_DEVICE_SELECT_QUERY = """
    SELECT d.id, d.hostname, d.ip_address, d.serial_number, dt.name AS device_type, v.name AS device_vendor, d.model, d.software_version, d.status, d.priority
    FROM devices d
    JOIN device_types dt 
    ON d.type_id = dt.id
    JOIN vendors v
    ON d.vendor_id = v.id
    WHERE {condition};
    """

@overload
def _get_devices(condition: str, params: dict[str, Any], many: bool = False) -> dict[str | Any]: ...

@overload
def _get_devices(condition: str, params: dict[str, Any], many: bool = True) -> list[dict[str | Any]]: ...

def _get_devices(condition: str, params: dict[str, Any], many: bool):
    """
    Shared function used to get devices from DB based on provided condition
    """
    engine = connect_to_database()

    try:
        with engine.connect() as conn:
            result = conn.execute(
                text(BASE_DEVICE_SELECT_QUERY.format(condition=condition)),
                params
            )
            data = result.mappings().fetchall() if many else result.mappings().fetchone()
    except Exception as e:
        raise RuntimeError("Database error while fetching devices") from e
    finally:
        engine.dispose()

    if not data:
        raise ValueError("No devices found")
    
    return data

def get_device_by_ip(ip_address: str) -> dict[str, Any]:
    """
    Get device from DB by IP_address
    """
    return _get_devices(
        condition="d.ip_address = :ip_address",
        params={"ip_address": ip_address},
        many=False
    )

def get_devices_by_vendor(vendor: str) -> list[dict[str,Any]]:
    """
    Get list of devices from DB by vendor
    """
    return _get_devices(
        condition="v.name = :vendor",
        params={"vendor": vendor.lower()},
        many=True
    )
