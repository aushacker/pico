import time
from machine import Pin, SPI
from SDCard import *

time.sleep(1) # settle time

print("create SPI objects")
card = SDCard(0)
print(card)
print(card._spi)

card.initialize()

print(card)
#while True:
#    time.sleep(1)


