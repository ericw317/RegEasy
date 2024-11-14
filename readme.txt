#RegEasy#

This is a Windows registry parser that is inspired by RegRipper.
The goal of this software is to simplify the process of finding information in the Windows registry. There is a lot of information in there, and more often than not, you are only looking for specific pieces of information. This program will automatically search the registry for whatever relevant information you are looking for.

How to use:
When you start the program, you will have two initial options. 

1) Drive
You can choose to direct it to a specific drive (either the C drive or a mounted disk image of another system), and it will search for the registry files for you.

2) Registry File
With this option, you can enter the path directly to the registry file you want to parse.

After you select the initial option, you will be presented with a list of information to gather. Just choose one, and the program does the rest of the work. It will also give you an option to output the results to a text file if you wish.

IMPORTANT:
FOR BEST RESULTS THIS MUST BE RUN AS ADMINISTRATOR, otherwise you might run into errors
These registry hives this program can currently parse are the following:
- SAM
- SYSTEM
- SOFTWARE
- NTUSER.DAT

I will be adding more capabilities soon.
