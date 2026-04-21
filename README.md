# Overview

This Python-based tool is for injecting channel label data from a .bvef (BrainVision Electrode Format) file to an existing LSL-style configuration file. 

The program can be used via downloading and launching the compiled executable, found in the Releases tab.
This route involves no extra installation or configuration of Python or its modules.
(Those who wish can also view, download, and run the associated Python code directly)

<img width="350" height="229" alt="image" src="https://github.com/user-attachments/assets/f7266e13-3619-4134-b7f9-35d459da6f00" />

## Usage
1. Select your BVEF file containing channel locations and coordinates
2. Select your configuration file (generated via BrainVision LSL connectors: https://www.brainproducts.com/downloads/more-software/#lsl)
3. Inject
4. Re-Load the BrainVision LSL connector, this time using the "_modified.json" file produced by the Injector
5. Confirm that the channel labels are accurate to your montage PDF file
