#
# Support for SD Card functions.
# aushacker
# May 2024
#

import time
from machine import Pin, SPI

class Command:
    """Represents various SD Card commands."""

    def __init__(self, name: str, index: int, response=1):
        self._name = name
        self._index = index
        self._response = response
        
    def __str__(self) -> str:
        return f'{self._name}({self._response})'

    def encode(self, arg: int) -> bytearray:
        """Returns a bytearray(6) containing the SDCard command bytes."""

        # index and argument (5 bytes)
        result = bytearray()
        result.append(0x40 | self._index)
        result.extend(int.to_bytes(arg, 4, 'big'))
        
        # CMD0 and CMD8 require valid CRCs, others are ignored when SPI is used
        if self._index == 0:
            result.append(0x95)
        elif self._index == 8:
            result.append(0x87)
        else:
            result.append(1)

        return result

    def has_extra_response(self) -> bool:
        """Response types 3 & 7 have extra response data."""
        
        return (self._response == 3) or (self._response == 7)

class Response:
    """Data holder for the SD Card response."""
    
    def __init__(self, response: int, extra=None):
        self.response = response
        self.extra = extra

    def __str__(self) -> str:
        x = None if self.extra == None else f'{self.extra:#x}'
        return f'Response(0b{self.response:08b},{x})'

    def is_illegal_command(self) -> bool:
        return (self.response & 0b100) != 0

class SDCard:
    """A layer above the SPI hardware, manages the SD card state and data exchange."""

    commands = {
        'CMD0': Command('CMD0', 0),
        'CMD8': Command('CMD8', 8, 7),
        'CMD55': Command('CMD55', 55),
        'CMD58': Command('CMD58', 58, 3),
        'ACMD41': Command('ACMD41', 41, 3)
    }

    def __init__(self, spi=0, pin=17):
        self._type = 'Unknown'
        self._state = 'uninitialized'
        self._cs = Pin(pin, mode=Pin.OUT, value=1)
        self._spi = SPI(spi)
        self._spi.init(baudrate=400_000, polarity=0, phase=0, bits=8)

    def __str__(self) -> str:
        return f'Card(_type: {self._type} _state: {self._state})'

    def execute(self, cmd, arg=0, txdata=b''):
        """Run a command on the card and return a Response.""" 

        command = SDCard.commands[cmd]
        request = command.encode(arg)       # 6 bytes
        try:
            b = 0
            
            # Send command frame
            self._cs(0)
            self._spi.write(request)
            
            # Wait for first and possibly only, response byte
            for x in range(8):
                b = self._spi.read(1, 0xff)  # read from DI with DO high (8 bits)
                if b != b'\xff':
                    break
                elif x >= 8:
                    raise RuntimeError('No response within expected time frame')

            # Handle R3/R7 format responses
            if command.has_extra_response():
                return Response(int.from_bytes(b, 1, 'big'), int.from_bytes(self._spi.read(4, 0xff), 4, 'big'))
            else:
                return Response(int.from_bytes(b, 1, 'big'))

        finally:
            self._cs(1)

    def go_idle_state(self):
        """Send software reset."""

        for x in range(3):
            response = self.execute('CMD0')
            if response.response == 1:
                self._state = 'idle'
                return response

        # failed after 3 attempts...
        raise RuntimeError('Software reset (CMD0) failed 3 attempts')

    def initialize(self):
        """Reset card and transition to the ready state."""

        print('forcing card to native mode')
        self.reset()

        print('sending card to idle (CMD0)')
        print(self.go_idle_state())

        print('checking voltage (CMD8)')
        response = self.send_if_cond()
        print(response)

        if response.is_illegal_command():
            # Check for V1 card
            pass
        else:
            # Handle V2 card
            self._type = 'SDC V2'
            if (response.extra != 0x1AA):
                raise RuntimeError('Unusable card: voltage')
            else:
                # TODO should voltages be checked at this point?
                print('reading OCR (CMD58)')
                print(self.read_ocr())
                print('initializing card (ACMD41)')
                print(self.execute('CMD55'))
                response = self.initialize_card()
                print(response)
                if response.response == 1:
                    time.sleep_ms(500)
                    print(self.execute('CMD55'))
                    print(self.initialize_card())
                    
    def initialize_card(self):
        """Initialize card (ACMD41)."""

        return self.execute('ACMD41', 0x40000000)

    def read_ocr(self):
        """Read Operations Condition Register (OCR)."""

        return self.execute('CMD58')

    def reset(self):
        """Force card to enter native operating mode by sending 80 clocks with DO high."""

        try:
            for x in range(10):
                self._spi.write(b'\xff')
        finally:
            self._cs(1)

    def send_if_cond(self):

        return self.execute('CMD8', 0x1AA)
