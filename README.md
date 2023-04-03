# Motion table control

The motion table can be remotely controlled with the script `MotionTable_CPanel.py`.  This script must be from within the lab network.  This repository is set up on `ita-cr-01.fnal.gov` where the necessary version of python with all necewssary packages can be accessed but running `source setup.sh`.  Talk to any of the facility cooridnators to be added to the authorized users list for this computer.  This script presents a simple GUI which shows the current table position and lets the horrizontal and vertical position of the table to be set.  Units for the table position are in mm.  

Center coordinates are x~159.5 mm and y~146.5 mm
Box all the way to the right (in camera view) = 320 mm, all the way to the left = 0 mm. Box goes down to ~80 mm and up to ~200 mm.

If running this script on another computer than `ita-cr-01` the packages `tkinter` and `easymodbus` will need to be installed.  

# Integrated proton count

The total integrated number of protons delivered to ITA can be retrieved from ACNet using the `intagrateITA.py` script.  This script must be run from a computer with access to ACNet such as `ita-cr-01.fnal.gov`.  This script can be run with the same setup script as above, `source setup.sh`.  This script gives several options which can be seen by running the help with `python integrateITA_py3.py -h`.  