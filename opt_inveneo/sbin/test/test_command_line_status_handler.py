from __future__ import with_statement

import sys
import os

sys.path.append(os.path.realpath('.'))

import unittest
from command_line_status_handler import *

class TestCommandLineStatusHandler(unittest.TestCase):
    def testGetCurrentStatusWithOneDrive(self):
        cl = CommandLineStatusHandler("test/test_get_status_command1.py", "ignored")
        self.assertEqual(cl.getCurrentStatus(), 1)

    def testGetCurrentStatusWithTwoDrives(self):
        cl = CommandLineStatusHandler("test/test_get_status_command2.py", "ignored")
        self.assertEqual(cl.getCurrentStatus(), 2)

    def testSetCurrentStatusWithOneDrive(self):
        cl = CommandLineStatusHandler("ignored", "test/test_update_fake_status_command1.sh")
        assert not os.path.exists("status_output")
        try:
            cl.updateCurrentStatus()
            assert os.path.exists("status_output")
            with open("status_output") as f:
                   self.assertEqual(f.read(), "1\n")
        finally: 
            try:
                os.unlink("status_output")
            except:
                pass

    def testSetCurrentStatusWithTwoDrives(self):
        cl = CommandLineStatusHandler("ignored", "test/test_update_fake_status_command2.sh")
        assert not os.path.exists("status_output")
        try:
            cl.updateCurrentStatus()
            assert os.path.exists("status_output")
            with open("status_output") as f:
                   self.assertEqual(f.read(), "2\n")
        finally: 
            try:
                os.unlink("status_output")
            except:
                pass

if __name__ == '__main__':
    unittest.main()
