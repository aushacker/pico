import time
from machine import Pin, SPI
from SDCard import SDCard, Command

time.sleep(1) # settle time

c0 = SDCard.commands["CMD0"]
print(c0.encode(0))

c8 = SDCard.commands["CMD8"]
print(c8.encode(0x1AA))

print("done")
while True:
    time.sleep(1)

print("create SPI objects")
card = SDCard(0)

print("forcing card to native mode")
card.reset()

print("sending card to idle (CMD0)")
card.goIdleState()

print("done")
while True:
    time.sleep(1)


