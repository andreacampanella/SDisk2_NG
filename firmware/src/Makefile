MCU = atmega328p
F_CPU = 27000000UL
COMMON_FLAGS = -Wall -Os -Wno-deprecated-declarations -Wno-strict-aliasing -D__PROG_TYPES_COMPAT__ -D_SDISK_OLED_ \
               -fpack-struct -fshort-enums -std=gnu99 -fgnu89-inline -funsigned-char -funsigned-bitfields \
               -mmcu=$(MCU) -DF_CPU=$(F_CPU) -MMD -MP
ASM_FLAGS = -x assembler-with-cpp -mmcu=$(MCU) -MMD -MP -D_SDISK_OLED_
CC = avr-gcc
OBJCOPY = avr-objcopy
SIZE = avr-size
AVRDUDE = sudo avrdude
PROGRAMMER = -c arduino
PORT = -P /dev/ttyACM0
BAUD = -b 115200
PART = -p m328p
OUT_DIR = ../out
TARGET = sdisk2_oled
HEX_FILE = $(OUT_DIR)/$(TARGET).hex

C_SOURCES = oled.c SPI_routines.c SD_routines.c FAT32.c main.c
ASM_SOURCES = sub.S
OBJECTS = $(C_SOURCES:.c=.o) $(ASM_SOURCES:.S=.o)

all: $(HEX_FILE)

%.o: %.c
	$(CC) $(COMMON_FLAGS) -c -o $@ $<

%.o: %.S
	$(CC) $(ASM_FLAGS) -c -o $@ $<

$(TARGET).elf: $(OBJECTS)
	$(CC) -Wl,-Map,$(TARGET).map -mmcu=$(MCU) -D_SDISK_OLED_ -o $@ $(OBJECTS)

$(HEX_FILE): $(TARGET).elf
	@mkdir -p $(OUT_DIR)
	$(OBJCOPY) -R .eeprom -O ihex $< $@
	$(SIZE) --format=avr --mcu=$(MCU) $<

flash: $(HEX_FILE)
	$(AVRDUDE) $(PROGRAMMER) $(PORT) $(BAUD) $(PART) -U flash:w:$(HEX_FILE):i

clean:
	rm -f *.o *.d *.map *.elf $(HEX_FILE)

-include $(OBJECTS:.o=.d)

