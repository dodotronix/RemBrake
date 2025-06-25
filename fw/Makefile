DEVICE := /media/sdb1

## DO NOT CHANGE THE FOLLOWING PART UNLESS YOU KNOW WHAT YOU ARE DOING

ROOT := $(shell pwd)
LIB_VERSION   := 20250121
LIB_NAME 	  := adafruit-circuitpython-bundle-9.x-mpy-$(LIB_VERSION)
ADAFRUIT_LIBS := "https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases/download/$(LIB_VERSION)/$(LIB_NAME).zip"
GIT_LOCATIONS := "git@github.com:dodotronix/CircuitPython_LTC2943.git" "git@github.com:dodotronix/CircuitPython_MY9221.git"
GIT_FOLDER 	  := $(ROOT)/git_repos
GIT_MODULES   := $(ROOT)/git_modules

TARGET := $(ROOT)/target
TARGET_LIB_FOLDER := $(TARGET)/lib 


LOCAL_MODULES := "RemBrake_Core.py" \
			     "RemBrake_WaveKit.py" \
			     "code.py"


ADAFRUIT_MPYS := "adafruit_ticks.mpy" \
				 "adafruit_logging.mpy" \
				 "neopixel.mpy" \
				 "simpleio.mpy" 

ADAFRUIT_FOLDER_LIBS := "adafruit_motor" \
						"asyncio" \
						"adafruit_register" 

ADAFRUIT_BUNDLE_FOLDER := $(ROOT)/$(LIB_NAME)/lib

ADAFRUIT_SOURCES := $(addprefix $(ADAFRUIT_BUNDLE_FOLDER)/,$(ADAFRUIT_MPYS)) \
                    $(addprefix $(ADAFRUIT_BUNDLE_FOLDER)/,$(ADAFRUIT_FOLDER_LIBS))

LOCAL_SOURCES := $(addprefix $(ROOT)/,$(LOCAL_MODULES))


all:
	@printf 'Please before the first run open the Makefile and change the TARGET variable\n'
	@printf 'to match your path to the mounted device\n' 
	@printf '\n'
	@printf 'USAGE : make prepare  - downloads libraries and copies them to the TARGET folder \n'
	@printf '             upload   - uploads the prepared folder to the device specified in DEVICE variable \n'
	@printf '             clean    - removes all downloaded and created data \n'
			

$(LIB_NAME).zip:
	@wget $(ADAFRUIT_LIBS)

$(LIB_NAME):$(LIB_NAME).zip
	@7z x $<

$(GIT_FOLDER):
	@if [ ! -d "$@" ]; then \
		mkdir -p $@; fi

$(GIT_MODULES):
	@if [ ! -d $@ ]; then \
		mkdir -p $@; fi

clone: $(GIT_FOLDER) $(GIT_MODULES)
	@for location in $(GIT_LOCATIONS); do \
		name=$$(basename $$location .git); \
		if [ ! -d "$(GIT_FOLDER)/$$name" ]; then \
			printf "[INFO] Cloning $$location into $(GIT_FOLDER)/$$name\n"; \
			git clone $$location $(GIT_FOLDER)/$$name; \
		else \
			printf "[INFO] Pulling latest changes for $$name\n"; \
			git -C $(GIT_FOLDER)/$$name pull; \
		fi; \
		cp -r $(GIT_FOLDER)/$$name/$$name.py $(GIT_MODULES); \
	done

prepare: $(LIB_NAME) clone
	@if [ ! -d "$(TARGET_LIB_FOLDER)" ]; then \
		mkdir -p $(TARGET_LIB_FOLDER); \
	fi; \
	echo $(GIT_MODULES)/*.py
	printf "[INFO] Copying libraries into $(TARGET_LIB_FOLDER)\n"; \
	cp -r $(ADAFRUIT_SOURCES) $(TARGET_LIB_FOLDER); \
	cp -r $(LOCAL_SOURCES) $(TARGET); \
	cp -r $(GIT_MODULES)/*.py $(TARGET);

upload: prepare
	@printf "[INFO] Uploading $(TARGET) to $(DEVICE)\n"
	@cp -r $(TARGET)/* $(DEVICE)

.PHONY: clean prepare clone 

clean:
	@rm -rf *.zip
	@rm -rf $(GIT_FOLDER)
	@rm -rf $(GIT_MODULES)
	@rm -rf $(LIB_NAME)
	@rm -rf $(TARGET)

