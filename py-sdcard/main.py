import time
from machine import Pin, SPI
from SDCard import *

time.sleep(1) # settle time

print("create SPI objects")
card = SDCard(0)
print(card._spi)

print("forcing card to native mode")
card.reset()

print("sending card to idle (CMD0)")
print(card.go_idle_state())

print("checking voltage (CMD8)")
print(card.send_if_cond())

#r1 = Response(0x01)
#print(r1)

#r2 = Response(0x01, 0x12345678)
#print(r2)

print("done")
#while True:
#    time.sleep(1)


