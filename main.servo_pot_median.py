import serial
import time

# Pico
pico = serial.Serial(
    "/dev/ttyACM1",
    baudrate=1000000,
    timeout=1
)

# ST3215 sürücü
servo = serial.Serial(
    "/dev/ttyACM0",
    baudrate=1000000,
    timeout=1
)

servo.reset_input_buffer()
servo.reset_output_buffer()
servo.write_timeout=0

def write_byte(ID, address, value):
    print("PID IS BEING SENT!")
    packet = bytearray([
        0xFF,
        0xFF,
       ID,
        4,
        0x03,
        address,
        value
    ])

    checksum = (~sum(packet[2:])) & 0xFF
    packet.append(checksum)
    print(packet.hex())
    print("PID command:", packet.hex())
    servo.write(packet)

def move_servo(ID, pos):
    print("Command has been sent", ID, pos)
    speed= 3400
    acc= 254
    move_time=0
    packet = bytearray([
        0xFF,
        0xFF,
        ID,
        10,
        0x03,
        0x29,
        acc,
        pos & 0xFF,
        (pos >> 8) & 0xFF,
        move_time & 0xFF,
        (move_time >> 8) & 0xFF,
        speed & 0xFF,
        (speed >> 8) & 0xFF
    ])

    checksum = (~sum(packet[2:])) & 0xFF
    packet.append(checksum)
    print(packet.hex())
    import time
    t1 = time.time()
    servo.write(packet)
    print("Sending duration: ", time.time()-t1)

list1 = []
list2 = []
last_med1=None
last_med2=None
med1 = None
med2 = None
write_byte(1, 0x15, 180) #P
write_byte(1, 0x17, 0) #I
write_byte(1, 0x16, 50) #D
write_byte(2, 0x15, 180) #P
write_byte(2, 0x17,0) #I
write_byte(2, 0x16, 50) #D
write_byte(1, 0x25, 10)
write_byte(1, 0x27, 10)
write_byte(2, 0x25, 10)
write_byte(2, 0x27, 10)

while True:

    line = pico.readline()
    print("PICO: ", line)
    if line:

        try:
            text = line.decode().strip()
            print(text)

            # Gelen:
            # M1:25000 M2:40000

            parts = text.split()

            m1_value = int(parts[0].split(":")[1])
            m2_value = int(parts[1].split(":")[1])

            pos1 = int(m1_value * 4095 / 65535)
            pos2 = int(m2_value * 4095 / 65535)
            list1.append(pos1)
            list2.append(pos2)


            if (len(list1)) >=3 and (len(list2)) >= 3:

                if len(list1) == 3:
                    sorted_list1 = sorted(list1)
                    med1 = sorted_list1[1]

                elif len(list1) > 3:
                    sorted_list1 = sorted(list1[len(list1)-1:len(list1)-4:-1])
                    med1 = sorted_list1[1]


                if len(list2) == 3:
                    sorted_list2 = sorted(list2)
                    med2 = sorted_list2[1]

                elif len(list2) > 3:
                    sorted_list2 = sorted(list2[len(list2)-1:len(list2)-4:-1])
                    med2 = sorted_list2[1]


                # Pico 0-65535
                # Servo 0-4095




                print(
                    "Servo1:",
                    med1,
                    "Servo2:",
                    med2
               )


# Pot1 -> Servo ID 1
                if last_med1 is None or abs(med1 - last_med1) > 50:
                    print("M1 target:", med1)
                    move_servo(1, med1)
                    last_med1 = med1

# Pot2 -> Servo ID 2
                if last_med2 is None or abs(med2 - last_med2) > 50:
                    print("M2 target:", med2)
                    move_servo(2, med2)
                    last_med2 = med2

        except Exception as e:
          print("Error:", e)


    time.sleep(0.001)
