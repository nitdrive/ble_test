import random
import struct


def binary_to_decimal(binary):
    binary1 = binary
    decimal, i, n = 0, 0, 0
    while binary != 0:
        dec = binary % 10
        decimal = decimal + dec * pow(2, i)
        binary = binary // 10
        i += 1

    return decimal


def binary(num):
    # Struct can provide us with the float packed into bytes. The '!' ensures that
    # it's in network byte order (big-endian) and the 'f' says that it should be
    # packed as a float. Alternatively, for double-precision, you could use 'd'.
    packed = struct.pack('f', num)
    print(packed)
    print('Packed: %s' % repr(packed))

    # For each character in the returned string, we'll turn it into its corresponding
    # integer code point
    #
    # [62, 163, 215, 10] = [ord(c) for c in '>\xa3\xd7\n']
    integers = [ord(c) for c in packed.decode('utf-8')]
    print('Integers: %s' % integers)

    # For each integer, we'll convert it to its binary representation.
    binaries = [bin(i) for i in integers]
    print('Binaries: %s' % binaries)

    # Now strip off the '0b' from each of these
    stripped_binaries = [s.replace('0b', '') for s in binaries]
    print('Stripped: %s' % stripped_binaries)

    # Pad each byte's binary representation's with 0's to make sure it has all 8 bits:
    #
    # ['00111110', '10100011', '11010111', '00001010']
    padded = [s.rjust(8, '0') for s in stripped_binaries]
    print('Padded: %s' % padded)

    # At this point, we have each of the bytes for the network byte ordered float
    # in an array as binary strings. Now we just concatenate them to get the total
    # representation of the float:
    return ''.join(padded)


def int_from_bytes(byte_seq):
    print(int.from_bytes(byte_seq, "little"))


def hex_from_bytes(byte_seq):
    hex_val = byte_seq.hex()
    print(hex_val)
    if hex_val == "00":
        print("Equal")
    else:
        print("Not equal")


def dbus_to_convert():
    value = dbus.Array(
        [dbus.Byte(17), dbus.Byte(0), dbus.Byte(0), dbus.Byte(231), dbus.Byte(0), dbus.Byte(40), dbus.Byte(51)],
        signature=dbus.Signature('y'))

    print("value:%s" % ''.join([str(v) for v in value]))

    print("value:%s" % [bytes([v]) for v in value])

    print("value:%s" % [int(v) for v in value])


if __name__ == '__main__':
    int_from_bytes(b"\x00")
    hex_from_bytes(b"\x00")

    dbus_to_convert()
    # minvalue = 0
    # maxvalue = 10.0
    # inc = 0.1
    # print([struct.pack('<f', minvalue), struct.pack('<f', maxvalue), struct.pack('<f', inc)])
    # payload = bytes([0]) + struct.pack('<f', maxvalue) + struct.pack('<f', inc)
    # print(payload)
    #
    # payload = []
    # for c in "0.110.0":
    #     payload.append(c.encode())
    #
    # print(payload)
    #
    # flag = 11100000
    # print(binary_to_decimal(flag))
    # value = []
    # flags = bytes([224])
    # print("224 as bytes")
    # print(flags)
    # print("1, 32, 0 as bytes")
    # byte_val = bytes([1, 32, 0])
    # print(byte_val)
    # print(byte_val.hex())
    # for by in byte_val:
    #     print(type(by))
    #
    # value.append(flags)
    # hrate = random.randrange(60, 120)
    # print(hrate)
    # value.append(bytes([224, 125]))
    # print(value)
    # val = 125
    # print(val.to_bytes(2, 'little'))
    #
    # valstring = str(val)
    # for c in valstring:
    #     print(c.encode())
    #
    # bytes_data = [104, 101, 108, 108, 111]
    # print("".join(map(chr, bytes_data)))
    #
    # print("From Hex")
    # print(bytes.fromhex('012000'))
