# MonsterrhinoControl

# Prepare your Raspberry Pi 4 for using with Monsterrhino Control 

Download Raspberry Pi Desktop from https://www.raspberrypi.org/software/raspberry-pi-desktop/. Make sure you have a version that is supported by the touch display driver (https://4dsystems.com.au/gen4-4dpi-50ct-clb). Use a program of your choice (e.g. Raspberry Pi Imager, BalenaEtcher - **attention your image might not work due to the choosen software to burn the image!**) to burn the Raspberry Pi Destop image to a SD card. You can check the kernel version of your Raspian installation by typing ``` uname -a``` into a terminal, select the display driver accordingly. 

Depending on what you need you can either install both, display driver and CAN driver, or just the one you need.

## Download preinstalled images
You can download the already setup images from our FTP server:

* **Running Windows:** open a **File explorer** window and copy following into the address line:
  ``` ftp://monsterrhino: F3voxLdA@217.199.10.233/``` 
  You will be prompted to enter following password: **F3voxLdA**
  After successfully accessing the folder you can download either the image with touch display driver and CAN driver installed (**only** the touch display works here - no monitor) or only CAN driver installed.



## Install Monsterrhino RGB LED

To enable the use of your Monsterrhino RGB LED in compination with the Monsterrhino Contorl run following commands in a terminal to install the necessary packages:

```C++
sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel
sudo python3 -m pip install --force-reinstall adafruit-blinka  
sudo pip3 install rpi_ws281x  
```

You can use the provided minimum example **led.py** to test your setup: https://github.com/Monsterrhino/MonsterrhinoControl/python3_examples

[![500](http://img.youtube.com/vi/sliHqhePpDA/0.jpg)](http://www.youtube.com/watch?v=sliHqhePpDA "Controlling Monsterrhino RGB LED")

-----------------------------------------------------------------
**Attention**
Programs to control the Monsterrhino LED need to be executed as **root** e.g. run the example led program in a terminal:  
```C++
sudo python3 led.py 
```

## Install **gen4-4dpi-50ct-clb** display driver 

### Option 1

Simply download a Raspberry Pi **image** where the CAN and display is already set up and burn it to an SD card as described in under the first point.

### Option 2

Installing this driver can brake your installation! Before you try this back up all important files and install it before the CAN installation. The best is to start from a clean install of Raspian, we tried many version of Raspian, now Raspberry Pi OS, however the only one that did not cause trable during installation can be found here: **http://downloads.raspberrypi.org/raspbian_latest**. It is the **kernel version 4.19.97**.

The 5" display is manifactured by 4D Systems, the product number is: GEN4-4DPi-50CT-CLB. The install instruction can be found here: https://4dsystems.com.au/mwdownloads/download/link/id/198/

Different versions of the driver are available here: https://4dsystems.com.au/gen4-4dpi-50ct-clb

The instruction contains the download link to the install package matching the kernel described above: https:/4dsystems.com.au/media/downloads/4DPi/All/gen4-hats_4-19-97.tar.gz

Download this package to the host PC, make sure the kernel of your Raspian matches the driver (e.g. 4-19-97). To check the kernel on your Raspian system type: ```uname -a``` or ```uname -r```

If you use the Raspberry Pi via SSH send the downloaded package now to the Raspberry Pi. To do so navigate on the host PC to the download section and enter following into the terminal:

scp gen4-hats_4-19-97.tar.gz pi@192.168.32.111:/home/pi

On the remote SSH terminal navigate to ```cd /home/pi``` and enter ```sudo tar -xzvf gen4-hats_4-19-97.tar.gz -C /```

After installation poweroff the Raspberry Pi by typing: ```sudo poweroff```. Disconnect from power and connect the display as instructed by the manual and restart the the Raspberry Pi. Now you should see the terminal on the 5" display. Further instructions can be found in the manual of the manufacturer mentioned above. 


## Install CAN bus driver on SPI2

This step should be performed before installing the display driver, make sure you have the IP address of the Raspberry Pi (type ``` ifconfig ``` into the terminall to see the IP address), because after installing the display driver the HDMI will not work anymore, and you need to access the RPi via SSH (enable SSH first).

### Option 1

Simply download a Raspberry Pi **image** where the CAN (or CAN and display) is already set up and burn it to an SD card as described in under the first point. 

You can test the MonsterrhinoControl to MonsterrhinoMotion CAN connection right away with the provided minimal Python3 example **can_func.py** that you find here: https://github.com/Monsterrhino/MonsterrhinoControl/python3_examples

If you have a working CAN connection you should see the CAN Tx/Rx LEDs blink on the MonsterrhinoMotion and the Motor 1 should turn:

[![500](http://img.youtube.com/vi/5juU6CXMVWE/0.jpg)](http://www.youtube.com/watch?v=5juU6CXMVWE "Move relative over CAN")


### Option 2

Download the necessary overlay files from https://github.com/Monsterrhino/MonsterrhinoControl/overlays and place them in the ``` boot/overlays/``` folder:
```C++
sudo rm /boot/overlays/spi1-3cs.dtbo
sudo cp spi1-3cs.dtbo /boot/overlays/
```

And place the file **mcp2515-can4.dtbo** in the ``` boot/overlays/``` folder.
<br><br>

Open following file in the terminal by running ```sudo nano /boot/config.txt``` and add following lines at the end of the file:

```C++
dtoverlay=mcp2515-can4,oscillator=16000000,interrupt=25
dtoverlay=spi1-3cs,cs2_spidev=disabled
```

Save with Ctrl + O and then close with Ctrl + X. &nbsp;
<br><br>

**Install CAN utilites** and reboot the Raspberry Pi:

```C++
sudo apt-get install can-utils   
```
Initiate and test CAN:

```C++
sudo ip link set can0 up type can bitrate 1000000
```
Check CAN connection:

```C++
sudo ip -details -statistics link show can0 
```
now type in the terminal:

```C++
ifconfig
```

and you should see:

```C++
can0: flags=193<UP,RUNNING,NOARP>  mtu 16
        unspec 00-00-00-00-00-00-00-00-00-00-00-00-00-00-00-00  txqueuelen 10  (UNSPEC)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 0  bytes 0 (0.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0  
```

Use ```dmesg | grep -i spi``` to diagnose the SPI interface, the output should be:

```C++
[    0.316068] spi-bcm2835 fe204000.spi: could not get clk: -517
[    0.450159] 4d-hats spi0.0: 4d-hat registered, product code = b3
[    4.673633] mcp251x spi1.2 can0: MCP2515 successfully initialized.
```

To run the minimal python example provided you need to install following Python packages:
```C++
sudo pip3 install python-can
sudo pip3 install bitstring
```


### Option 3

Compile the overlay files by your self as described:

Create a file named **mcp2515-can4-overlay.dts** with following content:

```C++
/*
 * Device tree overlay for mcp251x/can4 on spi1.2 edited by gregor h
 */

/dts-v1/;
/plugin/;

/ {
    compatible = "brcm,bcm2835", "brcm,bcm2836", "brcm,bcm2708", "brcm,bcm2709";
    /* disable spi-dev for spi1.2 */
    fragment@0 {
        target = <&spi1>;
        __overlay__ {
            status = "okay";
            spidev@2{
                status = "disabled";
            };
        };
    };

    /* the interrupt pin of the can-controller */
    fragment@1 {
        target = <&gpio>;
        __overlay__ {
            can4_pins: can4_pins {
                brcm,pins = <25>;
                brcm,function = <0>; /* input */
            };
        };
    };

    /* the clock/oscillator of the can-controller */
    fragment@2 {
        target-path = "/clocks";
        __overlay__ {
            /* external oscillator of mcp2515 on spi1.2 */
            can4_osc: can4_osc {
                compatible = "fixed-clock";
                #clock-cells = <0>;
                clock-frequency  = <16000000>;
            };
        };
    };

    /* the spi config of the can-controller itself binding everything together */
    fragment@3 {
        target = <&spi1>;
        __overlay__ {
            /* needed to avoid dtc warning */
            #address-cells = <1>;
            #size-cells = <0>;
            can4: mcp2515@1 {
                reg = <2>;
                compatible = "microchip,mcp2515";
                pinctrl-names = "default";
                pinctrl-0 = <&can4_pins>;
                spi-max-frequency = <10000000>;
                interrupt-parent = <&gpio>;
                interrupts = <25 0x2>;
                clocks = <&can4_osc>;
            };
        };
    };
    __overrides__ {
        oscillator = <&can4_osc>,"clock-frequency:0";
        spimaxfrequency = <&can4>,"spi-max-frequency:0";
        interrupt = <&can4_pins>,"brcm,pins:0",<&can4>,"interrupts:0";
    };
};


```

On the Raspberry Pi 4 compile this file to the overlay file mcp2515-can4.dtbo by running following command (might be necessary to install a package):

```C++
dtc -O dtb -o mcp2515-can4.dtbo -b 0 -@ mcp2515-can4-overlay.dts
```

Place the file mcp2515-can4.dtbo in /boot/overlays/.

The touch display uses GPIO PIN 17 as interrupt (PENIRQ) for the touch screen, however this pin is also used as chip enable 1 (SPI1_CE1) for the SPI1 port. The CAN bus uses SPI1 with SPI1_CE2, so there is no need for GPIO 17, therefore we will use a modified driver that does not address this pin.
Next create a file named spi1-3cs-overlay.dts with following content:


```C++
/dts-v1/;
/plugin/;


/ {
    compatible = "brcm,bcm2835", "brcm,bcm2708", "brcm,bcm2709";

    fragment@0 {
        target = <&gpio>;
        __overlay__ {
            spi1_pins: spi1_pins {
                brcm,pins = <19 20 21>;
                brcm,function = <3>; /* alt4 */
            };

            spi1_cs_pins: spi1_cs_pins {
                brcm,pins = <18 16>;
                brcm,function = <1>; /* output */
            };
        };
    };

    fragment@1 {
        target = <&spi1>;
        frag1: __overlay__ {
            /* needed to avoid dtc warning */
            #address-cells = <1>;
            #size-cells = <0>;
            pinctrl-names = "default";
            pinctrl-0 = <&spi1_pins &spi1_cs_pins>;
            cs-gpios = <&gpio 18 1>, <&gpio 17 1>, <&gpio 16 1>;
            status = "okay";

            spidev1_0: spidev@0 {
                compatible = "spidev";
                reg = <0>;      /* CE0 */
                #address-cells = <1>;
                #size-cells = <0>;
                spi-max-frequency = <500000>;
                status = "okay";
            };

            spidev1_1: spidev@1 {
                compatible = "spidev";
                reg = <1>;      /* CE1 */
                #address-cells = <1>;
                #size-cells = <0>;
                spi-max-frequency = <500000>;
                status = "okay";
            };

            spidev1_2: spidev@2 {
                compatible = "spidev";
                reg = <2>;      /* CE2 */
                #address-cells = <1>;
                #size-cells = <0>;
                spi-max-frequency = <500000>;
                status = "okay";
            };
        };
    };

    fragment@2 {
        target = <&aux>;
        __overlay__ {
            status = "okay";
        };
    };

    __overrides__ {
        cs0_pin  = <&spi1_cs_pins>,"brcm,pins:0",
               <&frag1>,"cs-gpios:4";
        cs1_pin  = <&spi1_cs_pins>,"brcm,pins:4",
               <&frag1>,"cs-gpios:16";
        cs2_pin  = <&spi1_cs_pins>,"brcm,pins:8",
               <&frag1>,"cs-gpios:28";
        cs0_spidev = <&spidev1_0>,"status";
        cs1_spidev = <&spidev1_1>,"status";
        cs2_spidev = <&spidev1_2>,"status";
    };
}
```

On the Raspberry Pi 4 compile this file to the overlay file spi1-3cs.dtbo by running following command:

```C++
dtc -O dtb -o spi1-3cs.dtbo -b 0 -@ spi1-3cs-overlay.dts
```
Run following commands to replace the file in the correct directory:

```C++
sudo rm /boot/overlays/spi1-3cs.dtbo
sudo cp spi1-3cs.dtbo /boot/overlays/
```

Open following file in the terminal by running sudo nano /boot/config.txt and add following lines:

```C++
dtoverlay=mcp2515-can4,oscillator=16000000,interrupt=25
dtoverlay=spi1-3cs,cs2_spidev=disabled
```

Save with Ctrl + O and then close with Ctrl + X. &nbsp;

Install CAN utilites:

```C++
sudo apt-get install can-utils   
```
Initiate and test CAN:

```C++
sudo ip link set can0 up type can bitrate 1000000
```
Check CAN connection:

```C++
sudo ip -details -statistics link show can0 
```
now type in the terminal:

```C++
ifconfig
```

and you should see:

```C++
can0: flags=193<UP,RUNNING,NOARP>  mtu 16
        unspec 00-00-00-00-00-00-00-00-00-00-00-00-00-00-00-00  txqueuelen 10  (UNSPEC)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 0  bytes 0 (0.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0  
```

Use ```dmesg | grep -i spi``` to diagnose the SPI interface, the output should be:

```C++
[    0.316068] spi-bcm2835 fe204000.spi: could not get clk: -517
[    0.450159] 4d-hats spi0.0: 4d-hat registered, product code = b3
[    4.673633] mcp251x spi1.2 can0: MCP2515 successfully initialized.
```
It might be necessary to add following to ```sudo nano /etc/modules```:
```
can
```







