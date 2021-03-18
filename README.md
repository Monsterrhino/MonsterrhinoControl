# MonsterrhinoControl

# Prepare your Raspberry Pi 4 for using with Monsterrhino Control 

Download Raspberry Pi Desktop from https://www.raspberrypi.org/software/raspberry-pi-desktop/. Make sure you have a version that is supported by the touch display driver (https://4dsystems.com.au/gen4-4dpi-50ct-clb). Use a program of your choice (e.g. Raspberry Pi Imager, BalenaEtcher - **attention your image might not work due to the choosen software to burn the image!**) to burn the Raspberry Pi Destop image to a SD card.

Depending on what you need you can either install both, display driver and CAN driver, or just the one you need.

## Install Monsterrhino RGB LED

To enable the use of your Monsterrhino RGB LED in compination with the Monsterrhino Contorl run following commands in a terminal to install the necessary packages:

```C++
sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel
sudo python3 -m pip install --force-reinstall adafruit-blinka  
sudo pip3 install rpi_ws281x  

```

You can use the provided minimum example **led.py** to test your setup: https://github.com/Monsterrhino/MonsterrhinoControl/python3_examples

[![500](http://img.youtube.com/vi/sliHqhePpDA/0.jpg)](http://www.youtube.com/watch?v=sliHqhePpDA "Controlling Monsterrhino RGB LED")


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
It might be necessary to add following to ```sudo nano /etc/modules```:
```
can
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


## Install **gen4-4dpi-50ct-clb** display driver 

The 5" display is manifactured by 4D Systems, the product number is: GEN4-4DPi-50CT-CLB. The install instruction can be found here: https://4dsystems.com.au/mwdownloads/download/link/id/198/

Different versions are available here: https://4dsystems.com.au/gen4-4dpi-50ct-clb

The instruction contains the download link to the install package: https:/4dsystems.com.au/media/downloads/4DPi/All/gen4-hats_4-19-97.tar.gz

Download this package to the host PC, make sure the kernel of your Raspian matches the driver (e.g. 4-19-97). To check the kernel on your Raspian system type: uname -a

Now we want to send the downloaded package to the Raspberry Pi. To do so navigate on the host PC to the download section and enter following into the terminal:

scp gen4-hats_4-19-97.tar.gz pi@192.168.32.111:/home/pi

On the remote SSH terminal navigate to cd /home/pi and enter sudo tar -xzvf gen4-hats_4-19-97.tar.gz -C /

After installation poweroff the Raspberry Pi by typing: sudo poweroff. Disconnect from power and connect the display as instructed by the manual and restart the the Raspberry Pi. Now you should see the terminal on the 5" display.



## CAN bus communication

### How to compose a CAN message for the MonsterrhinoMotion card
Commands can also be send over the CAN bus, therefore it is necessary to set the correct bits in the CAN frame.Following a description of the bits within the CAN frame.

	21-28 ID  (8 Bit 0-255 0=broadcast 1-9 Bus controller )
	15-20 Function (6 Bit )
	9-14 Nr (6 Bit )
	2-8  Sub Function (7 Bit)
	1   RTR respond
	
	Implementation protocol V2:
	-Addressing
		  - Used frame format is extended (29 bit) Address 0-536.870.911
			- Bit 0-3 Nummer (0-15)
			- Bit 4-13	sub command (9 bit =512)	    ;select sub command
			- Bit 14-17	command (0-15)					;command
				0 ('s')									;Sytem
				1 ('m')									;Motor
				2 ('i')									;Input
				3 ('f')									;User function
			- Bit 18	error						; active low
			-Bit 19-23	to Address
				0										;is a Broadcast message				
				2-31									;to Address
			-Bit 24-28	from Address
				0										;Bus controller
				2-31									;from Address
			- Bit 29	dentifies respond message
				0										;respond message
				1										;send message
			- Address range:
				Address 0 = broadcast message
				Address 1 = Bus controller
				available address range for client is 2-31

		

	-Data Field
		-Byte MSB-0		user return function_ID (0-127)
						Bit 0-7 (0-127)					;return function_ID
						Bit 7							; Set 1 = Get Value
		-Byte MSB-1 & MSB-7 <Data>		;length and type depending on the register

	


		- subCommand of motor command
			0;	emergency stop
				-no data
			1;	stop
				-no data
			2;	enable/disable driver
				-data type <byte>
					0:disabel driver
					1:enable driver
			3;  RampMode (uint8) <Set><Get>											RampMode
				-data type <uint8>
					0:																Positioning mode (using all A, D and V parameters)
					1:																Velocity mode to positive VMAX (using AMAX acceleration)
					2:																Velocity mode to negative VMAX (using AMAX acceleration)
					3:																Hold mode (velocity remains unchanged,unless stop event occurs)
			4;	TargetPosition (int48) <Set><Get>									the target position (step*1000) /!\ Set all other motion profile parameters before
				-data type <double*1000>
			5;	TargetPosition Register (int32) <Set><Get>							the target position (micro steps) /!\ Set all other motion profile parameters before
				-data type <int32>
			6;	MoveRelative(int32) <Set>											Move motor relative (steps*1000)
				-data type <double*1000>
			7;	MoveRelative Register(int32) <Set>									Move motor relative (micro steps)
				-data type <int32>
			8;	CurrentPosition (int48) <Set><Get>					 				the current internal position (steps*1000)
				-data type <double*1000>
			9;	CurrentPosition Register (int32) <Set><Get>					 		the current internal position (micro steps)
				-data type <micro steps>
			10;	Max Speed (uint32) <Set>											the max speed VMAX
				-data type <float*1000>
			11;	Max Speed Register (uint32) <Set><Get>								Register max speed VMAX
				-data type <uint32>
			12; Ramp speed Start(uint32) <Set><Get>									the start ramp speed
				-data type <float*1000>
			13;	Ramp speed Start Register (uint32) <Set><Get>						Register Ramp speed Start
				-data type <uint32>
			14; Ramp speed Stop(uint32) <Set><Get>									the stop ramp speed
				-data type <float*1000>
			15;	Ramp speed Stop Register (uint32) <Set><Get>						Register Ramp speed Stop
				-data type <uint32>
			16; Ramp speed Hold(uint32) <Set><Get>									the hold ramp speed
				-data type <float*1000>
			17;	Ramp speed Hold Register (uint32) <Set><Get>						Register Ramp speed Hold
				-data type <uint32>
			18;	get Current Speed(uint32)	<Get>									Return the current speed
				-data type <float*1000>
			19;	get Current Speed Register (uint32) <Get>							Return the current  speed Register 
				-data type <uint32>
			20; Acceleration AMAX(uint32) <Set><Get>								 ramp accelerations AMAX
				-data type <float*1000>
			21;	 Acceleration AMAX Register(uint32) <Set><Get>						Register  Acceleration AMAX
				-data type <uint32>
			22; Acceleration DMAX (uint32) <Set><Get>								ramp accelerations DMAX
				-data type <float*1000>
			23;	 Acceleration DMAX Register(uint32) <Set><Get>						Register  Acceleration DMAX
				-data type <uint32>
			24; Acceleration A1(uint32) <Set><Get>									ramp accelerations A1
				-data type <float*1000>
			25;	 Acceleration A1 Register(uint32) <Set><Get>						Register  Acceleration A1
				-data type <uint32>
			26; Acceleration D1(uint32) <Set><Get>									ramp accelerations D1
				-data type <float*1000>
			27;	 Acceleration D1 Register(uint32) <Set><Get>						Register  Acceleration D1
				-data type <uint32>
			28; ModeChangeSpeeds pwmThrs(uint32) <Set><Get>							mode change speeds pwmThrs
				-data type <float*1000>
			28;	 ModeChangeSpeeds pwmThrs Register(uint32) <Set><Get>				Register  ModeChangeSpeeds pwmThrs
				-data type <uint32>
			30; ModeChangeSpeeds coolThrs(uint32) <Set><Get>						mode change speeds coolThrs
				-data type <float*1000>
			21;	 ModeChangeSpeeds coolThrs Register(uint32) <Set><Get>				Register ModeChangeSpeeds coolThrs
				-data type <uint32>
			32; ModeChangeSpeeds highThrs(uint32) <Set><Get>						mode change speeds highThrs
				-data type <float*1000>
			33;	 ModeChangeSpeeds highThrs Register(uint32) <Set><Get>				Register ModeChangeSpeeds highThrs
				-data type <uint32>
			34;	Encoder Position (int48) <Set><Get>									the current encoder position (micro steps)
				-data type <double*1000>
			35;	Encoder Position Register(uint32) <Set><Get>						the current encoder position (steps*1000)
				-data type <uint32>
			36;	Latched Position (int48) <Set><Get>									the current latched position (micro steps)
				-data type <double*1000>
			37;	Latched Position Register(uint32) <Set><Get>						the Latched position (steps*1000)
				-data type <uint32>
			38;	LatchedEncoderPosition (int48) <Set><Get>							the current latched encoder position (steps*1000)
				-data type <double*1000>
			39;	LatchedEncoderPosition Register(int32) <Set><Get>					the current latched encoder position (uSteps)
				-data type <int32>


			50;	EncoderResolution_motorSteps (int32) <Set><Get>						the number of steps per turn for the motor
				-data type <int32>
			51;	EncoderResolution_encResolution (int32) <Set><Get>					the actual encoder resolution (pulses per turn)
				-data type <int32>
			
			53;	EncoderIndexConfiguration (uint8 bit bit bit bit ) <Set>			Configure the encoder N event context.
				-data type <uint8>													sensitivity : set to one of ENCODER_N_NO_EDGE, ENCODER_N_RISING_EDGE, ENCODER_N_FALLING_EDGE, ENCODER_N_BOTH_EDGES
				-data type <bit>													nActiveHigh : choose N signal polarity (true for active high)
				-data type <bit>													ignorePol : if true, ignore A and B polarities to validate a N event
				-data type <bit>													aActiveHigh : choose A signal polarity (true for active high) to validate a N event
				-data type <bit>													bActiveHigh : choose B signal polarity (true for active high) to validate a N event
				-data type <bit>
			54;	EncoderLatching(uint8) <Set>										Enable/disable encoder and position latching on each encoder N event (on each revolution)
				-data type <uint8>
			55;	isEncoderDeviationDetected(uint8) <Get>								Check if a deviation between internal pos and encoder has been detected
				-data type <uint8>
			56; clearEncoderDeviationFlag() <Set>									Clear encoder deviation flag (deviation condition must be handled before)
				-no data
			57; EncoderAllowedDeviation (int32) <Set>								Encoder Allowed Deviation
				-data type <uint32>
			58; SW_Mode (uint16) <Set><Get>											Reference Switch & StallGuard2 Event Configuration Register; See the TMC 5160 datasheet page 43
				-data type <uint16>
			59; DRV STATUS(uint32) <Get>											StallGuard2 Value and Driver Error Flags; datasheet page 56
				-data type <uint32>
			60; GetRampStatus(uint16) <Get><Reset>									RAMP_STAT � Ramp & Reference Switch Status Register; datasheet page 44
				-data type <uint16>
			61; GetGstat(uint8) <Get><Reset>										Global status flags
				-data type <uint8>



			67; SenseResistor(uint16) <Set><Get>									sense Resistor in mOhms 0=automatic
					-data type <uint16>
			68; MotorCurrent(uint16) <Set><Get>										Motor Current in mA
					-data type <uint16>
			69; MotorCurrentReduction(uint16) <Set><Get>							Motor current reduction in mA
					-data type <uint16>
			70; Motor Freewheeling Mode(uint8) <Set><Get>							Motor freewheeling mode
					-data type <uint8>
						FREEWHEEL_NORMAL   = 0x00,									Normal operation
						FREEWHEEL_ENABLED  = 0x01,									Freewheeling
						FREEWHEEL_SHORT_LS = 0x02,									Coil shorted using LS drivers
						FREEWHEEL_SHORT_HS = 0x03									Coil shorted using HS drivers
			71; Iholddelay(uint8) <Set><Get>										Controls the number of clock cycles for motor power down after a motion as soon as standstill is
																					detected (stst=1) and TPOWERDOWN has expired.The smooth transition avoids a motor jerk upon power down.
						-data type <uint8>
							0:														instant power down
							1..15:													Delay per current reduction step in multiple	of 2^18 clocks
			72; PWM_OFS(uint8) <Set><Get>											user defined PWM amplitude offset (0-255) related to full
						-data type <uint8>
																					motor current (CS_ACTUAL=31) in stand still.(Reset default=30)
			73; PWM_GRAD(uint8) <Set><Get>											Velocity dependent gradient for PWM amplitude: PWM_GRAD * 256 / TSTEP
																					This value is added to PWM_AMPL to compensate for	the velocity-dependent motor back-EMF.
						-data type <uint8>
			74; StepperDirection(uint8) <Set><Get>									Velocity motor  Stepper Direction
						-data type <uint8>

			75; UnLook Motor(uint8) <Set><Get>										Unlock Motor
				-data type <uint8>	
																This value is added to PWM_AMPL to compensate for	the velocity-dependent motor back-EMF.


			90; Homing Mode(uint8) <Set/Start><Get>									Start homing
						-data type <uint8>
							1: // endswitsh left
							2: // endswitsh right
			91; Homing timeOut (uint32) <Set><Get>									homing time to fail
						-data type <uint32>
			92; Homing maxPos (uint32) <Set><Get>									maximal deviation Posipion to fail
						-data type <uint32>
			93; Homing rampSpeed (uint32) <Set><Get>								rampSpeed for the homing process
						-data type <float*1000>
			94; Homing rampSpeed Register (uint32) <Set><Get>						Register rampSpeed for the homing process
						-data type <uint32>
			95; Homing rampSpeed_2(uint32) <Set><Get>								rampSpeed phase 2
						-data type <float*1000>
			96; Homing rampSpeed_2 Register (uint32) <Set><Get>						Register rampSpeed_2 for the homing process phase 2
						-data type <uint32>
			97; Homing Offset(uint48) <Set><Get>									homing offset(microstep)
						-data type <float*1000>
			98; Homing Offset Register (uint32) <Set><Get>							Register homing offset(microstep)
						-data type <uint32>
			99; Homing rampSpeedStart(uint32) <Set><Get>							homing ramp speed start
						-data type <double*1000>
			100; Homing rampSpeedStart Register (uint32) <Set><Get>					Register rampSpeedStart()
						-data type <uint32>
			101; Homing rampSpeedStop(uint32) <Set><Get>							homing ramp speed stop
						-data type <float*1000>
			102; Homing rampSpeedStop Register (uint32) <Set><Get>					Register rampSpeedStop()
						-data type <uint32>
			103; Homing rampSpeedHold(uint32) <Set><Get>							homing ramp speed hold
						-data type <float*1000>
			104; Homing rampSpeedHold Register (uint32) <Set><Get>					Register rampSpeedHold()
						-data type <uint32>
			105; Homing accelerationsAmax(uint32) <Set><Get>						homing accelerations Amax
						-data type <float*1000>
			106; Homing accelerationsAmax Register (uint32) <Set><Get>				Register accelerationsAmax()
						-data type <uint32>
			107; Homing accelerationsDmax(uint32) <Set><Get>			 			homing accelerations Dmax
						-data type <float*1000>
			108; Homing accelerationsDmax Register (uint32) <Set><Get>				Register accelerationsDmax()
						-data type <uint32>
			109 ;Homing accelerationsA1(uint32) <Set><Get>							homing accelerations A1
						-data type <float*1000>
			110; Homing accelerationsA1 Register (uint32) <Set><Get>				Register accelerationsA1()
						-data type <uint32>
			111;Homing accelerationsD1(uint32) <Set><Get>			 				homing accelerations D1
						-data type <float*1000>
			112; Homing accelerationsD1 Register (uint32) <Set><Get>				Register accelerationsD1()
						-data type <uint32>
										

			128;Startup  drvStrength(uint32) <Set><Get>			 					Startup Selection of gate driver current. Adapts the gate driver current to the gate charge of the external MOSFETs.
				-data type <uint8>
					00: weak
					01: weak+TC (medium above OTPW level)
					10: medium
					11: strong
						
			129;Startup  bbmClks(uint32) <Set><Get>			 						Startup 0..15: Digital BBM time in clock cycles (typ. 83ns).The longer setting rules (BBMTIME vs. BBMCLKS).
					-data type <uint16>
						(Reset Default: OTP 4 or 2)
			130;Startup  bbmTime(uint32) <Set><Get>			 						Startup Break-Before make delay
				-data type <uint8>
					0=shortest (100ns) � 16 (200ns) � 24=longest (375ns)
					>24 not recommended, use BBMCLKS instead
			131;Startup  Iholddelay(uint8) <Set><Get>								Startup	Iholddelay
						-data type <uint8>
			132;Startup  SenseResistor(uint16) <Set><Get>							Startup sense resistor in mOhms 0=automatic
					-data type <uint16>
			133;Startup  MotorCurrent(uint16) <Set><Get>							Startup motor current in mA
					-data type <uint16>
			134;Startup  MotorCurrentReduction(uint16) <Set><Get>					Startup motor current reduction in mA
					-data type <uint16>
			135;Startup  Motor Freewheeling Mode(uint8) <Set><Get>					Startup motor freewheeling mode
					-data type <uint8>
			136;Startup  PWM_OFS(uint8) <Set><Get>									Startup	user defined PWM amplitude offset (0-255) related to full
						-data type <uint8>
			137;Startup  PWM_GRAD(uint8) <Set><Get>									Startup	Velocity dependent gradient for PWM amplitude: PWM_GRAD * 256 / TSTEP
						-data type <uint8>
			138;Startup  StepperDirection(uint8) <Set><Get>							Startup	Velocity motor  Stepper Directio
						-data type <uint8>
			139;Startup  MaxSpeed (uint32) <Set><Get>								Startup	the max speed VMAX
				-data type <float*1000>
			140;Startup  MaxSpeed Register (uint32) <Set><Get>						Register Startup  MaxSpeed
						-data type <uint32>
			141;Startup  StartRampSpeed(uint32) <Set><Get>							Startup	the start ramp speed
				-data type <float*1000>
			142;Startup  StartRampSpeed Register (uint32) <Set><Get>				Register Startup  start ramp speed
						-data type <uint32>
			143;Startup  StopRampSpeed(uint32) <Set><Get>							Startup	the stop ramp speed
				-data type <float*1000>
			144;Startup  StopRampSpeed Register (uint32) <Set><Get>					Register Startup  stop ramp speed
						-data type <uint32>
			145;Startup  HoldRampSpeed(uint32) <Set><Get>							Startup	the hold ramp speed
				-data type <float*1000>
			146;Startup  HoldRampSpeed Register (uint32) <Set><Get>					Register Startup  hold ramp speed
					-data type <uint32>
			147;Startup  Acceleration maxAccel(uint32) <Set><Get>					Startup	ramp accelerations AMAX
				-data type <float*1000>
			148;Startup  Acceleration maxAccel Register (uint32) <Set><Get>			Register Startup  Acceleration maxAccel
					-data type <uint32>
			149;Startup  Acceleration maxDecel(uint32) <Set><Get>					Startup	ramp accelerations DMAX
				-data type <float*1000>
			150;Startup  Acceleration maxDecel Register (uint32) <Set><Get>			Register Startup  Acceleration maxDecel
					-data type <uint32>
			151;Startup  Acceleration startAccel(uint32) <Set><Get>					Startup	ramp accelerations A1
				-data type <uifloat*1000nt32>
			152;Startup  Acceleration startAccel Register (uint32) <Set><Get>		Register Startup  Acceleration startAccel
					-data type <uint32>
			153;Startup  Acceleration stopAccel(uint32) <Set><Get>					Startup	ramp accelerations D1
				-data type <float*1000>
			154;Startup  Acceleration stopAccel Register (uint32) <Set><Get>		Register Startup  Acceleration stopAccel
					-data type <uint32>
			155;Startup  ModeChangeSpeeds pwmThrs(uint32) <Set><Get>				Startup	mode change speeds pwmThrs
				-data type <float*1000>
			156;Startup  ModeChangeSpeeds pwmThrs Register (uint32) <Set><Get>		Register Startup  ModeChangeSpeeds pwmThrs
					-data type <uint32>
			157;Startup  ModeChangeSpeeds coolThrs(uint32) <Set><Get>				Startup	mode change speeds coolThrs
				-data type <float*1000>
			158;Startup  ModeChangeSpeeds coolThrs Register (uint32) <Set><Get>		Register Startup  ModeChangeSpeeds coolThrs
					-data type <uint32>
			159;Startup  ModeChangeSpeeds highThrs(uint32) <Set><Get>				Startup	mode change speeds highThrs
				-data type <float*1000>
			160;Startup  ModeChangeSpeeds highThrs Register (uint32) <Set><Get>		Register Startup  ModeChangeSpeeds highThrs
					-data type <uint32>
			161;Startup  EncoderResolution_motorSteps (int32) <Set><Get>		Startup	the number of steps per turn for the motor
				-data type <int32>
			162;Startup  EncoderResolution_encResolution (int32) <Set><Get>		Startup	the actual encoder resolution (pulses per turn)
				-data type <int32>
			
			164;Startup  EncoderIndexConfiguration (uint8 bit bit bit bit ) <Set><Get>		Startup	Configure the encoder N event context.
				-data type <uint8>													sensitivity : set to one of ENCODER_N_NO_EDGE, ENCODER_N_RISING_EDGE, ENCODER_N_FALLING_EDGE, ENCODER_N_BOTH_EDGES
				-data type <bit>													nActiveHigh : choose N signal polarity (true for active high)
				-data type <bit>													ignorePol : if true, ignore A and B polarities to validate a N event
				-data type <bit>													aActiveHigh : choose A signal polarity (true for active high) to validate a N event
				-data type <bit>													bActiveHigh : choose B signal polarity (true for active high) to validate a N event
				-data type <bit>													Startup	Enable/disable encoder and position latching on each encoder N event (on each revolution)
			
			166;Startup  EncoderAllowedDeviation (int32) <Set><Get>				Startup	Encoder Allowed Deviation
				-data type <uint32>
			167;Startup  SW_Mode (uint16) <Set><Get>							Startup	Reference Switch & StallGuard2 Event Configuration Register; See the TMC 5160 datasheet page 43
				-data type <uint16>
			168;Startup  RampMode (uint8) <Set><Get>							Startup	 RampMode
				-data type <uint8>
					0:															Positioning mode (using all A, D and V parameters)
					1:															Velocity mode to positive VMAX (using AMAX acceleration)
					2:															Velocity mode to negative VMAX (using AMAX acceleration)
					3:															Hold mode (velocity remains unchanged,unless stop event occurs)
				"HomingMode","HomingOffset","HomingMaxPos","HomingTimeout","HomingSpeed_2","HomingDmax"
			169;Startup  Homing Mode(uint8) <Set><Get>							Startup	homing mode
						-data type <uint8>
			170;Startup  Homing Offset(int48) <Set><Get>						Startup	homing offset(microstep)
						-data type <double*1000>
			171;Startup  Homing Offset Register (int32) <Set><Get>				Register Startup	homing offset(microstep)
						-data type <int32>
			172;Startup  Homing timeOut (uint32) <Set><Get>						Startup	homing time to fail
						-data type <uint32>
			173;Startup  Homing maxPos (int32) <Set><Get>						Startup	homing maximal deviation Posipion to fail
						-data type <int32>
			174;Startup  Homing rampSpeed_2(uint32) <Set><Get>					Startup	homing rampSpeed phase 2
						-data type <float*1000>
			175;Startup  Homing rampSpeed_2 Register (int32) <Set><Get>			Register homing Startup	rampSpeed_2
						-data type <int32>
			176;Startup  Homing accelerationsDmax(uint32) <Set><Get>			Startup	homing accelerations Dmax
						-data type <float*1000>
			175;Startup  Homing accelerationsDmax Register (int32) <Set><Get>	Register homing Startup	accelerationsDmax
						-data type <int32>
			512..768	Maping Motor Register
						-data type <int32/uint32>

			- subCommand of userFunction 
				1; start user function(uint8)  <Set><Get>							Start userFunction whith sub user function data
					-data type <uint8>
				2; stop user function
			   30; userFunctionVariable1(uint32)  <Set><Get>						Set/Get userFunction variable 1
			   31; userFunctionVariable2(uint32)  <Set><Get>						Set/Get userFunction variable 2
			   32; userFunctionVariable3(uint32)  <Set><Get>						Set/Get userFunction variable 3
			   33; userFunctionVariable4(uint32)  <Set><Get>						Set/Get userFunction variable 4
			   34; userFunctionVariable5(uint32)  <Set><Get>						Set/Get userFunction variable 5
			   35; userFunctionVariable6(uint32)  <Set><Get>						Set/Get userFunction variable 6
			   40; userFunction Variable1 float(uint48)(uint48/1000= double )  <Set><Get>					Set/Get userFunction float variable 1
			   41; userFunction Variable2 float(uint48)(uint48/1000= double )  <Set><Get>					Set/Get userFunction float variable 2
			   42; userFunction Variable3 float(uint48)(uint48/1000= double )  <Set><Get>					Set/Get userFunction float variable 3
			   43; userFunction Variable4 float(uint48)(uint48/1000= double )  <Set><Get>					Set/Get userFunction float variable 4

			   50; Startup  start user function(uint8)  <Set><Get>					Startup userFunction whith sub user function data

			   60; Startup userFunction Variable1(uint32)  <Set><Get>				Startup Set/Get userFunction variable 1
			   61; Startup userFunction Variable2(uint32)  <Set><Get>				Startup Set/Get userFunction variable 2
			   62; Startup userFunction Variable3(uint32)  <Set><Get>				Startup	Set/Get userFunction variable 3
			   63; Startup userFunction Variable4(uint32)  <Set><Get>				Startup	Set/Get userFunction variable 4
			   64; Startup userFunction Variable5(uint32)  <Set><Get>				Startup	Set/Get userFunction variable 5
			   65; Startup userFunction Variable6(uint32)  <Set><Get>				Startup	Set/Get userFunction variable 6
			   70; Startup userFunction Variable1 float(uint48)(uint48/1000= double )  <Set><Get>			Startup	Set/Get userFunction float variable 1
			   71; Startup userFunction Variable2 float(uint48)(uint48/1000= double )  <Set><Get>			Startup	Set/Get userFunction float variable 2
			   72; Startup userFunction Variable3 float(uint48)(uint48/1000= double )  <Set><Get>			Startup	Set/Get userFunction float variable 3
			   73; Startup userFunction Variable4 float(uint48)(uint48/1000= double )  <Set><Get>			Startup	Set/Get userFunction float variable 4

			- subCommand of input											<Input1..6 and laser1..2 >
				1 inputFaling(uint32)	<Set><Get>									Input Faling INPUT_RUN_USERFUNCTION
					-data type <uint32>
				2 inputRising(uint32)	<Set><Get>									Input Rising INPUT_RUN_USERFUNCTION
					-data type <uint32>
				3 Startup inputFaling(uint32)	<Set><Get>							Startup Input Faling INPUT_RUN_USERFUNCTION
					-data type <uint32>
				4 Startup inputRising(uint32)	<Set><Get>							Startup Input Rising INPUT_RUN_USERFUNCTION
					-data type <uint32>

				5 GetInputState <uint8><Get>										Get the state of input
					-data type <uint8>

				descipion of INPUT_RUN_USERFUNCTION:
				all fuctions can cominate 
				INPUT_RUN_USERFUNCTION_START_1						0x0001xx	; Start userfunction 1 whit sub function xx
				INPUT_RUN_USERFUNCTION_START_2						0x000200	; Start userfunction 2 whit sub function xx
				INPUT_RUN_USERFUNCTION_START_3						0x000400	; Start userfunction 3 whit sub function xx
				INPUT_RUN_USERFUNCTION_START_4						0x000800	; Start userfunction 4 whit sub function xx
				INPUT_RUN_USERFUNCTION_START_5						0x001000	; Start userfunction 4 whit sub function xx
				INPUT_RUN_USERFUNCTION_START_6						0x002000	; Start userfunction 4 whit sub function xx

				INPUT_RUN_USERFUNCTION_STOP_1						0x010100	; Stop userfunction 1
				INPUT_RUN_USERFUNCTION_STOP_2						0x010200	; Stop userfunction 2
				INPUT_RUN_USERFUNCTION_STOP_3						0x010400	; Stop userfunction 3
				INPUT_RUN_USERFUNCTION_STOP_4						0x010800	; Stop userfunction 4
				INPUT_RUN_USERFUNCTION_STOP_5						0x011000	; Stop userfunction 5
				INPUT_RUN_USERFUNCTION_STOP_6						0x012000	; Stop userfunction 6

				INPUT_RUN_MOTOR_STOP_1								0x020100	; Motor Stop 1
				INPUT_RUN_MOTOR_STOP_2								0x020200	; Motor Stop 2
				INPUT_RUN_MOTOR_STOP_3								0x020200	; Motor Stop 3
				INPUT_RUN_MOTOR_STOP_4								0x020400	; Motor Stop 4

				INPUT_RUN_MOTOR_EMERGENCYSTOP_1						0x022100	; EMERGENCYSTOP Motor  1
				INPUT_RUN_MOTOR_EMERGENCYSTOP_2						0x022200	; EMERGENCYSTOP Motor  1
				INPUT_RUN_MOTOR_EMERGENCYSTOP_3						0x022400	; EMERGENCYSTOP Motor  1
				INPUT_RUN_MOTOR_EMERGENCYSTOP_4						0x022800	; EMERGENCYSTOP Motor  1

