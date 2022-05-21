import serial #pip3 install pyserial
import time
import string
import subprocess

State_of_Charge = 0
voltage_level = 0
battery_capacity = 0
current_level = 0
remaining_sec = 0
remaining_time = 0

subprocess.run(['sudo', 'chmod', '777', '/dev/ttyUSB0'])

def hexdata(split_strings):
    print('[{}]'.format(', '.join(hex(x) for x in split_strings)))

def calculate_checksum(split_strings):
    checksum = 0
    for i in split_strings[:-2]:
        checksum += i
    print("checksum = ",checksum % 256,"check_digit=",split_strings[15])
    return checksum % 256 == split_strings[15]
    
def State_of_Charge(split_strings):
    State_of_Charge = split_strings[1]
    print("State_of_Charge =",State_of_Charge,"%")

def voltage_level(split_strings):
    voltage_level = split_strings[2]<<8 | split_strings[3]
    print("voltage_level =",voltage_level/100,"V")

def battery_capacity(split_strings):
    battery_capacity = int('0x' + ''.join([format(c, '02X') for c in split_strings[4:8]]),16) / 1000
    print("battery_capacity =",battery_capacity,"Ah")

def current_level(split_strings):
    current_level = int('0x' + ''.join([format(c, '02X') for c in split_strings[8:12]]),32)
    if current_level >= 0x80000000:
        current_level -= 0x100000000
    print("current_level =",current_level,"mA")
    print("current_level =",current_level/1000,"A")

def convert(seconds):
    min, sec = divmod(seconds, 60)
    hour, min = divmod(min, 60)
    return "%d:%02d:%02d" % (hour, min, sec)

def remaining_time(split_strings):
    remaining_sec = int('0x' + ''.join([format(c, '02X') for c in split_strings[12:15]]),16)
    print("remaining_sec =",remaining_sec,"s")
    remaining_time = convert(remaining_sec)
    print("remaining_time =",remaining_time)

#sudo chmod 777 /dev/ttyS0
port="/dev/ttyUSB0" #(jetson)port="/dev/ttyTHS1" | (pi zero) port="/dev/ttyS0"
ser=serial.Serial(port, baudrate=9600,bytesize=8, parity='N', stopbits=1,timeout=0.5)

while True:
    split_strings = []
    n=2
    try:
        newdata_hex=ser.readline().hex()
        print("newdata_hex",newdata_hex)
    except:
        pass

    #newdata_hex= "a55709e40000145e000001410022561500"
    
    while newdata_hex.startswith("a5") and len(newdata_hex)<34:
        print(newdata_hex,"len=", len(newdata_hex))
        newdata_hex = ''.join((newdata_hex,ser.readline().hex()))
        print("combined data=",newdata_hex,"len=", len(newdata_hex))

    # if newdata_hex.startswith("a5") and len(newdata_hex)<32:
    #     print(newdata_hex,"len=", len(newdata_hex))
    #     newdata_hex = ''.join((newdata_hex,ser.readline().hex()))
    #     print("combined data=",newdata_hex,"len=", len(newdata_hex))

    if not newdata_hex.startswith("a5") or len(newdata_hex)>34:
        print(newdata_hex,"len=", len(newdata_hex))
        print("no correct data received")
        print("========================================")
    else:
        print(newdata_hex,"len=", len(newdata_hex))
        for index in range(0,len(newdata_hex),n):
            split_strings.append(int(newdata_hex[index : index + n],16))

        check_check_digit = calculate_checksum(split_strings)
        print("valid data=",check_check_digit)
        print("========================================")
        if check_check_digit == True:
            hexdata(split_strings)
            print(split_strings)
            
            State_of_Charge(split_strings)
            voltage_level(split_strings)
            battery_capacity(split_strings)
            current_level(split_strings)
            remaining_time(split_strings)
            print("========================================")
