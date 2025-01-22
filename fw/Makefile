
LIB_VERSION:=20250121
LIB_NAME:=adafruit-circuitpython-bundle-9.x-mpy-$(LIB_VERSION)
ADAFRUIT_LIBS:="https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases/download/$(LIB_VERSION)/$(LIB_NAME).zip"
LIBS:= 

all:
	@printf 'USAGE : make prepare \n'

$(LIB_NAME).zip:
	@wget $(ADAFRUIT_LIBS)

$(LIB_NAME):$(LIB_NAME).zip
	@7z x $<

prepare: $(LIB_NAME)
	echo "Copy the libraries we need to the CIRCUITPY/lib folder"

clean:
	@rm -rf *.zip
	@rm -rf $(LIB_NAME)


