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
        self.name = name
        self.index = index
        self.response = response
        
    def __str__(self) -> str:
        return f"{self.name}({self.response})"

    def encode(self, arg: int) -> bytearray:
        """Returns a bytearray(6) containing the SDCard command bytes."""

        # index and argument (5 bytes)
        result = bytearray()
        result.append(0x40 | self.index)
        result.extend(int.to_bytes(arg, 4, 'big'))
        
        # CMD0 and CMD8 require valid CRCs, others are ignored
        if self.index == 0:
            result.append(0x95)
        elif self.index == 8:
            result.append(0x87)
        else:
            result.append(0)

        return result

    #
    def executeOn(self, card, arg, data):
        pass

class SDCard:
    """A layer above the SPI hardware, manages the SD state and data exchange."""

    commands = {
        "CMD0": Command("CMD0", 0),
        "CMD8": Command("CMD8", 8, 7)
    }

    def __init__(self, spi=0, pin=17):
        """ 
        Parameters
        ----------
        spi : int
            SD card command name
        arg : int
            Unsigned 32 bit integer argument 
        data : bytearray
            Optional data to append to the command, not all commands support this.

        """
        self.cs = Pin(pin, mode=Pin.OUT, value=1)
        self.spi = SPI(spi)
        self.spi.init(baudrate=400_000, polarity=0, phase=0, bits=8)

    def execute(self, cmd, arg, data=b''):
        """ 
        Parameters
        ----------
        cmd : str
            SD card command name
        arg : int
            Unsigned 32 bit integer argument 
        data : bytearray
            Optional data to append to the command, not all commands support this.

        Raises
        ------
        
        """
        command = commands[cmd]
        response = command.executeOn(self, arg, data)
        
        try:
            self.cs(0)
            self.spi.write(outBuff) 
            for x in range(9):
                response = self.spi.read(1, 0xff)           # read response
                if response == b'\xff':
                    if x < 9:
                        continue
                    else:
                        raise Error("No response")
                if response == b'\x01':
                    break
                raise ValueError(response)
        finally:
            self.cs(1)

    #
    # Run CMD0
    #
    # Returns a Response.
    #
    def goIdleState(self):
        return execute("CMD0", 0)
    
    #
    # Force card to enter native operating mode by sending 80 clocks with DO high
    #
    def reset(self):
        try:
            for x in range(10):
                self.spi.write(b'\xff')
        finally:
            self.cs(1)
