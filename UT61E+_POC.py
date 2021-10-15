import hid as hid
import time
from ctypes import *

with hid.Device(0x10C4, 0xEA80) as h:

    acu = []

    RANGE_RESISTANCE = [
        "Ω", #220.00Ω
        "KΩ", #2.2000KΩ
        "KΩ", #22.000KΩ
        "KΩ", #220.00KΩ
        "MΩ", #2.2000MΩ
        "MΩ", #22.000MΩ
        "MΩ"  #220.00MΩ
    ]

    RANGE_FREQUENCY = [
        "Hz", #22.00Hz
        "Hz", #220.0Hz
        "kHz", #22.000KHz
        "kHz", #220.00KHz
        "MHz", #2.2000MHz
        "MHz", #22.000MHz
        "MHz"  #220.00MHz
    ]

    RANGE_CAPACITANCE = [
        "nF", #22.000nF
        "nF", #220.00nF
        "µF", #2.2000μF
        "µF", #22.000μF
        "µF", #220.00μF
        "mF", #2.2000mF
        "mF", #22.000mF
        "mF"  #220.00mF
    ]

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
        if (acu[3] == 0x00): return "AC Voltage"
        elif (acu[3] == 0x01): return "AC Voltage"
        elif (acu[3] == 0x02): return "DC Voltage"
        elif (acu[3] == 0x03): return "DC Voltage"
        elif (acu[3] == 0x04): return "Frequency"
        elif (acu[3] == 0x05): return "Duty"
        elif (acu[3] == 0x06): return "Resistance"
        elif (acu[3] == 0x07): return "Continuity"
        elif (acu[3] == 0x08): return "Diodes"
        elif (acu[3] == 0x09): return "Capacitance"
        elif (acu[3] == 0x0C): return "DC Current"
        elif (acu[3] == 0x0D): return "AC Current"
        elif (acu[3] == 0x0E): return "DC Current"
        elif (acu[3] == 0x0F): return "AC Current"
        elif (acu[3] == 0x10): return "DC Current"
        elif (acu[3] == 0x11): return "AC Current"
        elif (acu[3] == 0x12): return "hFE"
        elif (acu[3] == 0x14): return "NCV"
        elif (acu[3] == 0x18): return "AC Voltage LPF"
        elif (acu[3] == 0x19): return "DC+AC"

    def parse_unit():

        if ((acu[3] == 0x00) | (acu[3] == 0x02) | (acu[3] == 0x08) |
            (acu[3] == 0x18) | (acu[3] == 0x19)): return "V"
        elif ((acu[3] == 0x01) | (acu[3] == 0x03)): return "mV"
        elif (acu[3] == 0x04): return RANGE_FREQUENCY[acu[4]&0xF]
        elif (acu[3] == 0x05): return "%"
        elif (acu[3] == 0x06): return RANGE_RESISTANCE[acu[4]&0xF]
        elif (acu[3] == 0x07): return "Ω"
        elif (acu[3] == 0x09): return RANGE_CAPACITANCE[acu[4]&0xF]
        elif ((acu[3] == 0x0C) | (acu[3] == 0x0D)): return "μA"
        elif ((acu[3] == 0x0E) | (acu[3] == 0x0F)): return "mA"
        elif ((acu[3] == 0x10) | (acu[3] == 0x11)): return "A"
        elif (acu[3] == 0x12): return "β"

        return ""

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
    write_config([0x43, 0x03])

    write([ 0xab, 0xcd, 0x03, 0x5e, 0x01, 0xd9 ])
    read_raw()
    print("Maker ID: 0x" + ''.join('%02X'%i for i in acu[:2]))
    print("Response Lenght: 0x" + ''.join('%02X'%i for i in acu[2:3]))
    print("Selected Function: " + parse_func())
    print("Unit: " + parse_unit())
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
##
