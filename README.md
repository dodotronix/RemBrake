# RemBrake - remote brake system for handbikes 

![PCB picture](pics/introduction.png)

## Introduction
- TODO explain what the RemBrake, why we decided to create this project

### Assembling RemBrake
- TODO explain how to use the kicad data
- TODO how to solder the modules on the RemBrake PCB
- TODO how to connect the wires

### Prepare the module 
1) load the circuitpython to the QT Py RP2040
2) press and hold BOOT button and then press RST button
3) you should see now RPI partition mounted to your PC 
4) download CircuitPython bootloader (.uf2 file) from [circuitpython.org](https://circuitpython.org/board/adafruit_qtpy_rp2040/) 
5) drag and drop the file onto the partition
6) it takes few moments and you should see your partition name turn to CIRCUITPYTHON

### Upload RemBrake files + necessary modules
1) go to the folder fw folder
2) run $ make prepare
3) move the folder target to your CIRCPITPYTHON partition

## Features
- TODO how the PCB behaves (charging, running, error)
- TODO what the different colors mean

## Possible further development
- Bidirectional remote contoller that the assistant can see the battery status
- Accelerometer feedback, to adjust braking power according to the situation
- Using hydraulic piston actuator to move with the brake directly, which could shrink significantly the size of the package
- designing custom usb-c charger to avoid the hustle with unprecise power management of the chinese module

## Development
![PCB inactive breakout modules](pics/development/assembled_modules_inactive.jpg)
![PCB active breakout modules](pics/development/assembled_modules_active.jpg)
