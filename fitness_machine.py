import random

import dbus

from utils.gap.advertisement import Advertisement
from utils.gatt.profile import Application, Service, Characteristic, Descriptor

GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"
NOTIFY_TIMEOUT = 500


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


class FitnessMachineFeature(Characteristic):
    FITNESS_MACHINE_FEATURE_CHARACTERISTIC_UUID = "0x2ACC"

    def __init__(self, service):
        self.notifying = False

        Characteristic.__init__(
            self, self.FITNESS_MACHINE_FEATURE_CHARACTERISTIC_UUID,
            ["read"], service)

    def ReadValue(self, options):
        #                          <----------------------------------
        # fitnessMachineFeatures = 00000000 00000000 01000000 00000011
        #                          <----------------------------------
        # targetSettingFeatures =  00000000 00000000 11100000 00001100
        # fmfeaturesoctets = [00000011, 01000000, 00000000, 00000000] (little endian order)
        # targetSettingoctets = [00001100, 11100000, 00000000, 00000000] (little endian order)
        # Flags set based on Fitness Machine Service specification
        # Refer to: https://www.bluetooth.com/specifications/specs/fitness-machine-service-1-0/

        return bytes([3, 64, 0, 0, 12, 224, 0, 0])


class TrainingStatus(Characteristic):
    TRAINING_STATUS_CHARACTERISTIC_UUID = "0x2AD3"

    def __init__(self, service):
        self.notifying = False

        Characteristic.__init__(
            self, self.TRAINING_STATUS_CHARACTERISTIC_UUID,
            ["notify", "read"], service)

    def ReadValue(self, options):
        return bytes([3])

    def set_training_status_callback(self):
        if self.notifying:
            value = bytes([3])
            self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])

        return self.notifying

    def StartNotify(self):
        if self.notifying:
            return

        self.notifying = True
        self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": bytes([3])}, [])
        self.add_timeout(NOTIFY_TIMEOUT, self.set_training_status_callback)

    def StopNotify(self):
        self.notifying = False


class FitnessMachineControlPoint(Characteristic):
    pass


class FitnessMachineStatus(Characteristic):
    pass


class IndoorBikeData(Characteristic):
    pass


class SupportedResistanceLevelRange(Characteristic):
    pass


class SupportedPowerRange(Characteristic):
    pass


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
    app.add_service(HERLFitnessMachineService(1))
    app.register()

    adv = HERLParacycleAdvertisement(0)
    adv.register()

    print(app.services)

    try:
        app.run()
    except KeyboardInterrupt:
        app.quit()
