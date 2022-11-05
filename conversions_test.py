import random


def binary_to_decimal(binary):
    binary1 = binary
    decimal, i, n = 0, 0, 0
    while binary != 0:
        dec = binary % 10
        decimal = decimal + dec * pow(2, i)
        binary = binary // 10
        i += 1

    return decimal


if __name__ == '__main__':
    flag = 11100000
    print(binary_to_decimal(flag))
    value = []
    flags = bytes([224])
    print("224 as bytes")
    print(flags)
    print("1, 32, 0 as bytes")
    byte_val = bytes([1, 32, 0])
    print(byte_val)
    print(byte_val.hex())

    value.append(flags)
    hrate = random.randrange(60, 120)
    print(hrate)
    value.append(bytes([224, 125]))
    print(value)
    val = 125
    print(val.to_bytes(2, 'little'))

    valstring = str(val)
    for c in valstring:
        print(c.encode())

    bytes_data = [104, 101, 108, 108, 111]
    print("".join(map(chr, bytes_data)))

    print("From Hex")
    print(bytes.fromhex('012000'))
