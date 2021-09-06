import hid as hid
import time
from ctypes import *

with hid.Device(0x10C4, 0xEA80) as h:

    acu = []

    def write_config(data):
        """write configuration with send_feature_report"""
        len_bytes = len(data)
        buf = create_string_buffer(len_bytes)
        buf[:len_bytes] = data[:len_bytes]
        h.send_feature_report(buf)

    def write(data):
        len_bytes = len(data)
        buf = create_string_buffer(len_bytes + 1)
        # Store the length of data in buf[0]
        buf[0] = len_bytes
        buf[1:] = data[:len_bytes]
        h.write(buf)

    def read_raw():
        counter = 0
        while counter < 10:
            counter += 1
            time.sleep(0.10)
            b = h.read(2, 1)
            if len(b) > 0:
                acu.append(b[1])
                counter = 0

    def parse_func():
        if (acu[3] == 0x00): return "AC Voltage (V)"
        elif (acu[3] == 0x01): return "AC Voltage (mV)"
        elif (acu[3] == 0x02): return "DC Voltage (V)"
        elif (acu[3] == 0x03): return "DC Voltage (mV)"
        elif (acu[3] == 0x04): return "HZ"
        elif (acu[3] == 0x05): return "%"
        elif (acu[3] == 0x06): return "Resistance"
        elif (acu[3] == 0x07): return "Continuity"
        elif (acu[3] == 0x08): return "Diodes"
        elif (acu[3] == 0x09): return "Capacitance"
        elif (acu[3] == 0x0C): return "DC Current (uA)"
        elif (acu[3] == 0x0D): return "AC Current (uA)"
        elif (acu[3] == 0x0E): return "DC Current (mA)"
        elif (acu[3] == 0x0F): return "AC Current (mA)"
        elif (acu[3] == 0x10): return "DC Current (A)"
        elif (acu[3] == 0x11): return "AC Current (A)"
        elif (acu[3] == 0x12): return "hFE"
        elif (acu[3] == 0x14): return "NCV"
        elif (acu[3] == 0x18): return "AC LPF"
        elif (acu[3] == 0x19): return "DC+AC"

    def check_crc():
        crc_calc = sum(acu[:17])
        crc_dmm = acu[17] << 8 | acu[18]
        if (crc_calc == crc_dmm):
            return "OK"
        return "KO (got 0x{:X}".format(crc_calc) + ", should've been 0x{:X})".format(crc_dmm)

    def parse_flags():
        ret = ""
        if (acu[14] & 0x1): ret += "REL, "
        if (acu[14] & 0x2): ret += "HLD, "
        if (acu[14] & 0x4): ret += "MIN, "
        if (acu[14] & 0x8): ret += "MAX, "

        if (acu[15] & 0x4): ret += "MAN, "

        if (acu[16] & 0x2): ret += "PMIN, "
        if (acu[16] & 0x4): ret += "PMAX, "
        if (acu[16] & 0x8): ret += "UKW, " # Unknow

        return ret[:-2]

    h.get_feature_report(0x46, 64)

    write_config([0x41, 0x01])
    write_config([0x50, 0x00, 0x00, 0x25, 0x80, 0x00, 0x00, 0x03, 0x00])
    write_config([0x43, 0x43, 0x03])

    write([ 0xab, 0xcd, 0x03, 0x5e, 0x01, 0xd9 ])
    read_raw()
    print("Maker ID: 0x" + ''.join('%02X'%i for i in acu[:2]))
    print("Response Lenght: 0x" + ''.join('%02X'%i for i in acu[2:3]))
    print("Selected Function: " + parse_func())
    print("Range: 0x" + ''.join('%02X'% (i & 0x0F) for i in acu[4:5]))
    print("Value: " + ''.join('%c'%c for c in acu[5:12]))
    print("Analog Bar:", end = "")
    if (acu[16] & 0x1): print("-", end = "")
    print("|" + "---------|" * acu[12] + "-" * acu[13])
    print("Flags: " + parse_flags())
    print("CRC: " + check_crc())

##    print("Testing Select CMD")
##    time.sleep(2)
##    write([ 0xab, 0xcd, 0x03, 0x4c, 0x01, 0xc7 ])
##    time.sleep(2)
##    write([ 0xab, 0xcd, 0x03, 0x4c, 0x01, 0xc7 ])
##    time.sleep(2)
##
##    print("Testing Manual Range CMD")
##    write([ 0xab, 0xcd, 0x03, 0x46, 0x01, 0xc1 ])
##    time.sleep(2)
##    write([ 0xab, 0xcd, 0x03, 0x46, 0x01, 0xc1 ])
##    time.sleep(2)
##
##    print("Testing Auto Range CMD")
##    write([ 0xab, 0xcd, 0x03, 0x47, 0x01, 0xc2 ])
##    time.sleep(2)
##
##    print("Testing Relative Measure CMD")
##    write([ 0xab, 0xcd, 0x03, 0x48, 0x01, 0xc3 ])
##    time.sleep(2)
##    write([ 0xab, 0xcd, 0x03, 0x48, 0x01, 0xc3 ])
##    time.sleep(2)
##
##    print("Testing Hz / % CMD")
##    write([ 0xab, 0xcd, 0x03, 0x49, 0x01, 0xc4 ])
##    time.sleep(2)
##    write([ 0xab, 0xcd, 0x03, 0x49, 0x01, 0xc4 ])
##    time.sleep(2)
##    write([ 0xab, 0xcd, 0x03, 0x49, 0x01, 0xc4 ])
##    time.sleep(2)
##
##    print("Testing HLD CMD")
##    write([ 0xab, 0xcd, 0x03, 0x4a, 0x01, 0xc5 ])
##    time.sleep(2)
##    write([ 0xab, 0xcd, 0x03, 0x4a, 0x01, 0xc5 ])
##    time.sleep(2)
##
##    print("Testing Light CMD")
##    write([ 0xab, 0xcd, 0x03, 0x4b, 0x01, 0xc6 ])
##    time.sleep(2)
##    write([ 0xab, 0xcd, 0x03, 0x4b, 0x01, 0xc6 ])
##    time.sleep(2)
##
##    print("Testing Peak Max / Min CMD")
##    write([ 0xab, 0xcd, 0x03, 0x4d, 0x01, 0xc8 ])
##    time.sleep(2)
##    write([ 0xab, 0xcd, 0x03, 0x4d, 0x01, 0xc8 ])
##    time.sleep(2)
##
##    print("Testing Peak Off CMD")
##    write([ 0xab, 0xcd, 0x03, 0x4e, 0x01, 0xc9 ])
##    time.sleep(2)
##
##    print("Testing Max / Min CMD")
##    write([ 0xab, 0xcd, 0x03, 0x41, 0x01, 0xbc ])
##    time.sleep(2)
##    write([ 0xab, 0xcd, 0x03, 0x41, 0x01, 0xbc ])
##    time.sleep(2)
##
##    print("Testing Max / Min Off CMD")
##    write([ 0xab, 0xcd, 0x03, 0x42, 0x01, 0xbd ])



# These commands are not present on the official app I really don't know if they
# do anything appart from making the UT61E+ beep... be carefull because they could
# be doing something naughty

##    time.sleep(5)
##
##    print("Testing Hidden CMD 0x43")
##    write([ 0xab, 0xcd, 0x03, 0x43, 0x01, 0xbe ])
##    time.sleep(5)
##
##    print("Testing Hidden CMD 0x44")
##    write([ 0xab, 0xcd, 0x03, 0x43, 0x01, 0xbf ])
##    time.sleep(5)
##
##    print("Testing Hidden CMD 0x45")
##    write([ 0xab, 0xcd, 0x03, 0x45, 0x01, 0xc0 ])
##    time.sleep(5)
##
##    print("Testing Hidden CMD 0x4f")
##    write([ 0xab, 0xcd, 0x03, 0x4f, 0x01, 0xca ])
##    time.sleep(5)
