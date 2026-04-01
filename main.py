from src.get_from_db import get_device_by_ip, get_devices_by_vendor

def main():
    device = get_devices_by_vendor('test')
    print(device)


if __name__ == "__main__":
    main()