# MonsterrhinoControl

# Prepare your Raspberry Pi 4 for using with Monsterrhino Control 

Download Raspberry Pi Desktop from https://www.raspberrypi.org/software/raspberry-pi-desktop/. Make sure you have a version that is supported by the touch display driver (https://4dsystems.com.au/gen4-4dpi-50ct-clb). Use a program of your choice (e.g. BalenaEtcher) to burn the Raspberry Pi Destop image to a SD card.

### Install CAN bus driver on SPI2

This step should be performed after installing the display driver, make sure you have the IP address of the Raspberry Pi, because after installing the display driver the HDMI will not work anymore, and you need to access the RPi via SSH (enable SSH first). Idea from http://www.industrialberry.com/quad-can-bus-adapter-raspberry-canberry/, uncompiled files can be downloade there (also in the rpi_py_tc package):


```C++
mcp2515-can2-overlay.dts
```

Create a file named mcp2515-can4-overlay.dts with following content:

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

&nbsp;

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

