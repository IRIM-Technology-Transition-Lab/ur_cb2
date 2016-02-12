UR-Sockets:
===========
Testing and working with socket connections to the UR

License:
--------
You are not granted a license of any kind:
Copyright (c) 2016 GTRC. All rights reserved.

What is Provided:
-----------------

For Python Import:
..................

+--------+---------+-----------------------------------------------------------------+
| ur_cb2 |         | Provides high level access to basic UR Robot interfacing        |
+--------+---------+-----------------------------------------------------------------+
|        | receive | Provides low level access to allow receiving data from a UR CB2 |
+--------+---------+-----------------------------------------------------------------+
|        | send    |Provides low level access to allow sending data to a UR CB2      |
+--------+---------+-----------------------------------------------------------------+

- ur_cb2      :  Provides high level access to basic UR Robot interfacing
    - receive :  Provides low level access to allow receiving data from a UR CB2
    - send    :  Provides low level access to allow sending data to a UR CB2

For Command Line Usage:
.......................
>>>cb2-listen

Examples:
.........

:``cb2_robot_example.py``:
    An example script which will move a robot around. You should be careful
    about running this before ensuring that it will not lead to a crash
:``send/cb2_send_example.py``:
    An example script which will send movement commands to the robot. You
    should be careful about running this before ensuring that it will not
    lead to a crash
:``receive/cb2_receive_example.py``:
    An example script which will receive data from the robot. This is exposed
    on the command line.

How To Setup:
-------------
#. Go to the home screen of PolyScope
#. Click on `SETUP Robot`
#. Click on `Setup NETWORK`
#. Set the IP address, subnet mask, and default gateway to something
    intelligent, which matches the network on which the robot will be operating
#. Plug in the network cables.
#. Rock and roll (it is recommended to test by running `cb2-listen` from the
    command line)