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
        self.add_service_data("0x1826", dbus.Byte(bytes.fromhex('012000')))


class HERLFitnessMachineService(Service):
    HERL_FITNESS_MACHINE_UUID = "0x1826"

    def __init__(self, index):
        Service.__init__(self, index, self.HERL_FITNESS_MACHINE_UUID, True)
        self.add_characteristic(HeartRateMeasurementCharacteristic(self))
        self.add_characteristic(BodySensorLocation(self))
        self.add_characteristic(HeartRateUnitCharacteristic(self))


class FitnessMachineFeature(Characteristic):
    pass


class TrainingStatus(Characteristic):
    pass


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
