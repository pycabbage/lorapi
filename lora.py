from serial import Serial
import RPi.GPIO as GPIO
from struct import unpack
from time import sleep

ResetPin = 12

class LoRa():
    def __init__(self):
        print("lora:Setup __init__()")
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(ResetPin, GPIO.OUT)
        GPIO.output(ResetPin, 1)
        self.s = Serial('/dev/serial0', 115200) # シリアルポートを115200kbps, 8bit, Non parity, 1 stop-bitでオープン

    def reset(self):
        print("lora:Reset")
        GPIO.output(ResetPin, 0)
        sleep(0.1)
        GPIO.output(ResetPin, 1)

    def open(self):
        print("lora:Serial Open", end="")
        self.s.open()
        print("ed")

    def close(self):
        print("lora:Serial Close", end="")
        self.s.close()
        print("d")

    def readline(self, timeout = None):
        if timeout != None:
            self.close()
            self.s.timeout = timeout
            self.open()
        line = self.s.readline()
        if timeout != None:
            self.close()
            self.s.timeout = None
            self.open()
        return line

    def write(self, msg):
        print("lora:write \"", msg.replace("\r\n", "\\r\\n").replace("\n", "\\n"), "\".")
        self.s.write(msg.encode('utf-8'))

    def parse(self, line):
        print("lora:parse")
        fmt = '4s4s4s' + str(len(line) - 14) + 'sxx'
        data = unpack(fmt, line)
        # hex2i = lambda x: int(x, 16) if int(x, 16) <= 0x7fff else ~ (0xffff - int(x, 16)) + 1
        def hex2i(x):
            if int(x, 16) <= 0x7fff:
                return int(x, 16)
            else:
                return ~ (0xffff - int(x, 16)) + 1
        rssi = hex2i(data[0])
        panid = hex2i(data[1])
        srcid = hex2i(data[2])
        msg = data[3].decode('utf-8')
        return (rssi, panid, srcid, msg)

if __name__ == "__main__":
    lr = LoRa()
    print("Main start.")
    while True:
        data = lr.parse(lr.readline())
        print("Data :", data)
