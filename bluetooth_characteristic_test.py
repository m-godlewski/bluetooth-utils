import argparse
import time

from bluepy import btle


# script arguments parsing
parser = argparse.ArgumentParser()
parser.add_argument("-m", "--mac_address", type=str, help="MAC address of device.")
parser.add_argument("-s", "--service_uuid", type=str, help="Service UUID.")
parser.add_argument("-c", "--char_uuid", type=str, help="Characteristic UUID.")
args = parser.parse_args()


# custom delegate class
class CustomDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        print("A notification was received: %s" % data)


# peripheral instance
while True:
    print(100 * "-")

    try:
        # device instance
        device = btle.Peripheral(args.mac_address, btle.ADDR_TYPE_PUBLIC)
        device.setDelegate(CustomDelegate)

        # setup to turn notifications
        service = device.getServiceByUUID(args.service_uuid)
        characteristic = service.getCharacteristics(args.char_uuid)[0]

        print()
        print(characteristic)
        print(type(characteristic))
        print(characteristic.valHandle)
        print()

        device.writeCharacteristic(characteristic.valHandle + 1, b"\x01\x00")

        # waiting for notifications
        while True:
            if device.waitForNotifications(10.0):
                continue
            print("Waiting...")

    except Exception as e:
        time.sleep(2)
        print(e)
        pass
