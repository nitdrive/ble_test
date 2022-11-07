import random

import dbus

from utils.gap.advertisement import Advertisement
from utils.gatt.profile import Application, Service, Characteristic, Descriptor

GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"
NOTIFY_TIMEOUT = 500
import struct


class HERLParacycleAdvertisement(Advertisement):
    def __init__(self, index):
        Advertisement.__init__(self, index, "peripheral")
        self.add_local_name("HERL FM")
        self.include_tx_power = True
        self.add_service_uuid("0x1818")
        self.add_service_uuid("0x1826")
        # Set flags (8 bits) little endian represented with decimal 1, fitness machine (16 bits) little endian
        # represented with decimal numbers 32 and 0
        self.add_service_data("0x1826", bytes([1, 32, 0]))


class HERLFitnessMachineService(Service):
    HERL_FITNESS_MACHINE_UUID = "0x1826"

    def __init__(self, index):
        Service.__init__(self, index, self.HERL_FITNESS_MACHINE_UUID, True)
        self.add_characteristic(FitnessMachineFeature(self))
        self.add_characteristic(TrainingStatus(self))
        self.add_characteristic(FitnessMachineControlPoint(self))
        self.add_characteristic(FitnessMachineStatus(self))
        self.add_characteristic(IndoorBikeData(self))
        self.add_characteristic(SupportedResistanceLevelRange(self))
        self.add_characteristic(SupportedPowerRange(self))


class FitnessMachineFeature(Characteristic):
    FITNESS_MACHINE_FEATURE_CHARACTERISTIC_UUID = "0x2ACC"

    def __init__(self, service):
        self.notifying = False

        Characteristic.__init__(
            self, self.FITNESS_MACHINE_FEATURE_CHARACTERISTIC_UUID,
            ["read"], service)

    def ReadValue(self, options):
        #                          <---------------------------------- read from left to right
        # fitnessMachineFeatures = 00000000 00000000 01000000 00000011
        #                          <---------------------------------- read from left to right
        # targetSettingFeatures =  00000000 00000000 11100000 00001100
        # fmfeaturesoctets = [00000011, 01000000, 00000000, 00000000] (little endian order)
        # targetSettingoctets = [00001100, 11100000, 00000000, 00000000] (little endian order)
        # Flags set based on Fitness Machine Service specification
        # Refer to: https://www.bluetooth.com/specifications/specs/fitness-machine-service-1-0/
        # using the decimal value for each octet above to build a list and convert to bytes
        return bytes([3, 64, 0, 0, 12, 224, 0, 0])


class TrainingStatus(Characteristic):
    TRAINING_STATUS_CHARACTERISTIC_UUID = "0x2AD3"

    def __init__(self, service):
        self.notifying = False

        Characteristic.__init__(
            self, self.TRAINING_STATUS_CHARACTERISTIC_UUID,
            ["notify", "read"], service)

    def ReadValue(self, options):
        return bytes([2])

    def set_training_status_callback(self):
        if self.notifying:
            value = bytes([2])
            self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])

        return self.notifying

    def StartNotify(self):
        if self.notifying:
            return

        self.notifying = True
        self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": bytes([2])}, [])
        self.add_timeout(NOTIFY_TIMEOUT, self.set_training_status_callback)

    def StopNotify(self):
        self.notifying = False


class FitnessMachineControlPoint(Characteristic):
    FITNESS_MACHINE_CONTROL_POINT_CHARACTERISTIC_UUID = "0x2AD9"

    def __init__(self, service):
        self.notifying = False

        Characteristic.__init__(
            self, self.FITNESS_MACHINE_CONTROL_POINT_CHARACTERISTIC_UUID,
            ["indicate", "write"], service)

    def WriteValue(self, value, options):
        print("Received Value:")
        print(value)


class FitnessMachineStatus(Characteristic):
    FITNESS_MACHINE_STATUS_CHARACTERISTIC_UUID = "0x2ADA"

    def __init__(self, service):
        self.notifying = False

        Characteristic.__init__(
            self, self.FITNESS_MACHINE_STATUS_CHARACTERISTIC_UUID,
            ["notify"], service)

    # Todo: Set proper status values based on BLE specification
    def set_fitness_machine_status_callback(self):
        if self.notifying:
            value = bytes([2])
            self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])

        return self.notifying

    def StartNotify(self):
        if self.notifying:
            return

        self.notifying = True
        self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": bytes([2])}, [])
        self.add_timeout(NOTIFY_TIMEOUT, self.set_fitness_machine_status_callback)

    def StopNotify(self):
        self.notifying = False


class IndoorBikeData(Characteristic):
    INDOOR_BIKE_DATA_CHARACTERISTIC_UUID = "0x2AD2"

    def __init__(self, service):
        self.notifying = False

        Characteristic.__init__(
            self, self.INDOOR_BIKE_DATA_CHARACTERISTIC_UUID,
            ["notify"], service)

    def get_indoor_bike_data(self):
        value = []
        flags = bytes([224])  # b'\xe0'
        value.append(dbus.Byte(flags))
        hrate = random.randrange(60, 120)
        print("Heart Rate:" + str(hrate))
        value.append(dbus.Byte(bytes([hrate])))
        return value

    def set_indoor_bike_data_callback(self):
        if self.notifying:
            value = self.get_indoor_bike_data()
            self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])

        return self.notifying

    def StartNotify(self):
        if self.notifying:
            return

        self.notifying = True
        self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": self.get_indoor_bike_data()}, [])
        self.add_timeout(NOTIFY_TIMEOUT, self.set_indoor_bike_data_callback)

    def StopNotify(self):
        self.notifying = False


class SupportedResistanceLevelRange(Characteristic):
    SUPPORTED_RESISTANCE_LEVEL_CHARACTERISTIC_UUID = "0x2AD6"

    def __init__(self, service):
        self.notifying = False

        Characteristic.__init__(
            self, self.SUPPORTED_RESISTANCE_LEVEL_CHARACTERISTIC_UUID,
            ["read"], service)

    def ReadValue(self, options):
        minvalue = 0
        maxvalue = 100
        inc = 1
        payload = b"\x01\x64\x00"
        return bytes([0, 0, 208, 7, 1, 0])


class SupportedPowerRange(Characteristic):
    SUPPORTED_POWER_RANGE_CHARACTERISTIC_UUID = "0x2AD8"

    def __init__(self, service):
        self.notifying = False

        Characteristic.__init__(
            self, self.SUPPORTED_POWER_RANGE_CHARACTERISTIC_UUID,
            ["read"], service)

    def ReadValue(self, options):
        # min_power = 00000000 00000000 (0 W)
        # max_power = 00000111 11010000 (2000 W)
        # power_increments = 00000000 00000001 (1 W)
        power = [0, 0, 208, 7, 1, 0]
        return bytes(power)


if __name__ == '__main__':
    app = Application()
    app.add_service(HERLFitnessMachineService(1))
    app.register()

    adv = HERLParacycleAdvertisement(0)
    adv.register()

    print(app.services)

    try:
        app.run()
    except KeyboardInterrupt:
        app.quit()
