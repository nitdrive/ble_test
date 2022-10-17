#!/usr/bin/python3

"""Copyright (c) 2019, Douglas Otwell

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import random

import dbus

from utils.gap.advertisement import Advertisement
from utils.gatt.profile import Application, Service, Characteristic, Descriptor
from gpiozero import CPUTemperature
import math

GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"
NOTIFY_TIMEOUT = 1000


class HERLParacycleAdvertisement(Advertisement):
    def __init__(self, index):
        Advertisement.__init__(self, index, "peripheral")
        self.add_local_name("HERL Paracycle")
        self.include_tx_power = True


class GenericAccess(Service):
    GenericAccessUUID = "0x1800"

    def __init__(self, index):
        Service.__init__(self, index, self.GenericAccessUUID, True)
        self.add_characteristic(DeviceNameCharacteristic(self))
        self.add_characteristic(AppearanceCharacteristic(self))
        self.add_characteristic(PeripheralPreferredConnectionCharacteristic(self))


class DeviceNameCharacteristic(Characteristic):
    DeviceNameCharacteristic_UUID = "0x2A00"

    def __init__(self, service):
        Characteristic.__init__(
            self, self.DeviceNameCharacteristic_UUID,
            ["read"], service)

    def ReadValue(self, options):
        value = []

        val = "HERL HR"
        value.append(dbus.Byte(val.encode()))

        return value


class AppearanceCharacteristic(Characteristic):
    DeviceNameCharacteristic_UUID = "0x2A01"

    def __init__(self, service):
        Characteristic.__init__(
            self, self.DeviceNameCharacteristic_UUID,
            ["read"], service)

    def ReadValue(self, options):
        value = []

        val = bytes([833])
        value.append(dbus.Byte(val))

        return value


class PeripheralPreferredConnectionCharacteristic(Characteristic):
    PeripheralPreferredCharacteristic_UUID = "0x2A04"

    def __init__(self, service):
        Characteristic.__init__(
            self, self.PeripheralPreferredCharacteristic_UUID,
            ["read"], service)

    def ReadValue(self, options):
        value = []

        val = bytes([833])
        value.append(dbus.Byte(val))

        return value


class HERLHeartRateService(Service):
    HERL_HEART_RATE_SVC_UUID = "0x180D"

    def __init__(self, index):
        self.units = "BPM"

        Service.__init__(self, index, self.HERL_HEART_RATE_SVC_UUID, True)
        self.add_characteristic(HeartRateMeasurementCharacteristic(self))
        self.add_characteristic(BodySensorLocation(self))
        self.add_characteristic(HeartRateUnitCharacteristic(self))

    def get_units(self):
        return self.units


class HeartRateMeasurementCharacteristic(Characteristic):
    HEARTRATE_CHARACTERISTIC_UUID = "0x2A37"

    def __init__(self, service):
        self.notifying = False

        Characteristic.__init__(
            self, self.HEARTRATE_CHARACTERISTIC_UUID,
            ["notify"], service)
        # self.add_descriptor(HeartRateDescriptor(self))

    def get_heartrate(self):
        value = []
        flags = bytes([224])
        value.append(dbus.Byte(flags))
        hrate = random.randrange(60, 120)
        print("Heart Rate:" + str(hrate))
        value.append(dbus.Byte(bytes([hrate])))
        return value

    def set_heartrate_callback(self):
        if self.notifying:
            value = self.get_heartrate()
            self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])

        return self.notifying

    def StartNotify(self):
        if self.notifying:
            return

        self.notifying = True

        value = self.get_heartrate()
        self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])
        self.add_timeout(NOTIFY_TIMEOUT, self.set_heartrate_callback)

    def StopNotify(self):
        self.notifying = False

    def ReadValue(self, options):
        value = self.get_heartrate()

        return value


class HeartRateDescriptor(Descriptor):
    HEARTRATE_DESCRIPTOR_UUID = "2901"
    HEARTRATE_DESCRIPTOR_VALUE = "Heart Rate"

    def __init__(self, characteristic):
        Descriptor.__init__(
            self, self.HEARTRATE_DESCRIPTOR_UUID,
            ["read"],
            characteristic)

    def ReadValue(self, options):
        value = []
        desc = self.HEARTRATE_DESCRIPTOR_VALUE

        for c in desc:
            value.append(dbus.Byte(c.encode()))

        return value


class BodySensorLocation(Characteristic):
    UNIT_CHARACTERISTIC_UUID = "0x2A38"

    def __init__(self, service):
        Characteristic.__init__(
            self, self.UNIT_CHARACTERISTIC_UUID,
            ["read"], service)

    def ReadValue(self, options):
        value = []

        val = "Chest"
        value.append(dbus.Byte(val.encode()))

        return value


class HeartRateUnitCharacteristic(Characteristic):
    UNIT_CHARACTERISTIC_UUID = "00000001-710e-4a5b-8d75-3e5b444bc3cf"

    def __init__(self, service):
        Characteristic.__init__(
            self, self.UNIT_CHARACTERISTIC_UUID,
            ["read", "write"], service)
        self.add_descriptor(HeartRateUnitDescriptor(self))

    def WriteValue(self, value, options):
        print("Received Value:")
        print(value)
        # val = str(value[0]).upper()

    def ReadValue(self, options):
        value = []

        val = "BPM"
        value.append(dbus.Byte(val.encode()))

        return value


class HeartRateUnitDescriptor(Descriptor):
    UNIT_DESCRIPTOR_UUID = "2901"
    UNIT_DESCRIPTOR_VALUE = "Beats Per Minute (BPM)"

    def __init__(self, characteristic):
        Descriptor.__init__(
            self, self.UNIT_DESCRIPTOR_UUID,
            ["read"],
            characteristic)

    def ReadValue(self, options):
        value = []
        desc = self.UNIT_DESCRIPTOR_VALUE

        for c in desc:
            value.append(dbus.Byte(c.encode()))

        return value


if __name__ == '__main__':
    app = Application()
    app.add_service(HERLHeartRateService(1))
    app.register()

    adv = HERLParacycleAdvertisement(0)
    adv.register()

    print(app.services)

    try:
        app.run()
    except KeyboardInterrupt:
        app.quit()
