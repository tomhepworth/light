# light

# Components:

- Raspberry Pi (any)
- Pimoroni SPI LCD 1.3": https://shop.pimoroni.com/products/1-3-spi-colour-lcd-240x240-breakout?variant=30250963632211


# Dependencies:

### Python stuff:
`sudo apt update
sudo apt install python3-rpi.gpio python3-spidev python3-pip python3-pil python3-numpy`

### OLED display library:
`sudo pip3 install st7789`

Make sure I2C and SPI are enabled in raspi-config (sudo raspi-config) under Interface Options.