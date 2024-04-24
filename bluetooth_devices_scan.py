"""
This script is used for scanning nearby bluetooth devices and retrieve GATT profile.
"""

import argparse
import json

from bluepy.btle import Scanner, Peripheral, UUID


# time period that scanning will be performed
SCAN_TIME = 10


# script arguments parsing
parser = argparse.ArgumentParser()
parser.add_argument("-m", "--mac_address", type=str, help="MAC address of device.")
parser.add_argument(
    "-d", "--dump", type=bool, help="Dumps device characteristic to JSON file."
)
args = parser.parse_args()


def display_header(text: str) -> None:
    """Draws header with given text as title."""
    print(" ", 98 * "-", " ")
    print("|", text.center(98), "|")
    print(" ", 98 * "-", " ")


def display_device_data(device: Peripheral) -> None:
    """Displaying each bluetooth device service and it's characteristic."""
    # list of device services
    for service in device.getServices():
        print(
            "SERVICE UUID: {} COMMON NAME: [{}]".format(
                service.uuid, UUID(service.uuid).getCommonName()
            )
        )
        # lists of service characteristics
        print("\tCHARACTERISTICS:")
        for characteristic in service.getCharacteristics():
            print(
                "\t - UUID: {} HANDLE: {} (0x{}) - {} - [{}]".format(
                    characteristic.uuid,
                    characteristic.getHandle(),
                    characteristic.getHandle(),
                    characteristic.propertiesToString(),
                    UUID(characteristic.uuid).getCommonName(),
                )
            )
    print()
    # list of device descriptors
    for descriptor in device.getDescriptors():
        print(
            "DESCRIPTORS: {}, [{}], Handle: {}".format(
                descriptor.uuid,
                UUID(descriptor.uuid).getCommonName(),
                descriptor.handle,
            )
        )
    print()
    # list of device characteristics
    for characteristic in device.getCharacteristics():
        print(
            "DEVICE CHARACTERISTIC: {} [{}] (0x{}), {}, Value: {}".format(
                characteristic.uuid,
                characteristic.getHandle(),
                characteristic.getHandle(),
                characteristic.descs,
                characteristic.read() if characteristic.supportsRead() else "",
            )
        )
    print()


def dump_profile_to_json(device: Peripheral, mac_address: str) -> bool:
    """Saves given device GATT profile to JSON file."""
    try:
        file_content = {}
        # iterate over services
        for service in device.getServices():
            # current iteration service object
            file_content[str(service.uuid)] = {
                "common_name": UUID(service.uuid).getCommonName(),
                "characteristics": [],
            }
            # appending each service characteristic object to list
            for characteristic in service.getCharacteristics():
                file_content[str(service.uuid)]["characteristics"].append(
                    {
                        "uuid": str(characteristic.uuid),
                        "common_name": UUID(characteristic.uuid).getCommonName(),
                        "handle": characteristic.getHandle(),
                        "properties": characteristic.propertiesToString(),
                    }
                )
        # saves dictionary to JSON file
        with open(f"{mac_address}_bluetooth_profile.json", "w+") as f:
            json.dump(file_content, f)
    except Exception as e:
        print(e)
        return False
    else:
        return True


def scan_for_devices() -> list:
    """Scan for nearby bluetooth devices and returns their data as list."""
    devices = Scanner().scan(SCAN_TIME)
    print(f"Number of devices found = {len(devices)}")
    for device in devices:
        print(f"Device {device.addr} RSSI={device.rssi} dB")
        for _, desc, value in device.getScanData():
            print(f"\t{desc} = {value}")
    return devices


# main section
if __name__ == "__main__":
    # scans for nearby bluetooth devices
    display_header("Scan Results")
    devices_data = scan_for_devices()

    # if mac address has been specified retrieve bluetooth characteristic only from selected device
    if args.mac_address:
        display_header(text=f"Device '{args.mac_address}'")
        try:
            device = Peripheral(args.mac_address)
        except Exception as e:
            print(e)
            pass
        else:
            display_device_data(device)
            if args.dump:
                dump_profile_to_json(device=device, mac_address=args.mac_address)

    # otherwise, retrieve characteristic for each found device
    else:
        for device_data in devices_data:
            display_header(text=f"Device '{device_data.addr}'")
            try:
                device = Peripheral(device_data.addr)
            except Exception as e:
                print(e)
                pass
            else:
                display_device_data(device)
                if args.dump:
                    dump_profile_to_json(device=device, mac_address=device_data.addr)
