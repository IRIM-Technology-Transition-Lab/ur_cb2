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

For Command Line Usage:
.......................
View live status of robot:
>>>cb2-listen

Save points from robot for future use:
>>>cb2-record

Play back previously recorded points:
>>>cb2-play

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
#. Install the packages: `python setup.py install` or `pip install ur_cb2`
#. Go to the home screen of PolyScope
#. Click on `SETUP Robot`
#. Click on `Setup NETWORK`
#. Set the IP address, subnet mask, and default gateway to something
   intelligent, which matches the network on which the robot will be operating
#. Plug in the network cables.
#. Rock and roll (it is recommended to test by running `cb2-listen` from the
   command line)
#. Once everything is setup, you can import by: `import ur_cb2`,
   `import ur_cb2.receive`, and `import ur_cb2.send`

License:
--------
The MIT License (MIT)

Copyright (c) 2016 GTRC.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.