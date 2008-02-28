""" This module tests the functionality in the notification_decider that is the part
of the Inveneo system that makes sure we only send notifications in the right sitations"""

import sys
import os

sys.path.append(os.path.realpath('.'))

import unittest
import notification_decider

class NotificationDeciderTest(unittest.TestCase):
    def setUp(self):
        self.decider = notification_decider.NotificationDecider()

    def testDegeneratedArrayAndOneDriveExpected(self):
        assert not self.decider.isThisAnError("DegradedArray", 1)

    def testDegeneratedArrayAndTwoDrivesExpected(self):
        assert self.decider.isThisAnError("DegradedArray",2)

    def testDegeneratedArrayAndOneDriveShouldChangeStateInformation(self):
        assert not self.decider.shouldChangeStateInformation("DegradedArray",1)

    def testShouldChangeStateForDegeneratedWithTwoExpected(self):
        assert not self.decider.shouldChangeStateInformation("DegradedArray",2)

    def testShouldChangeStateForAddedWithOneExpected(self):
        assert self.decider.shouldChangeStateInformation("SpareActive",1)

    def testShouldNotChangeStateForAddedWithTwoExpected(self):
        assert not self.decider.shouldChangeStateInformation("SpareActive",2)

    def testShouldChangeStateForFailedWithOneExpected(self):
        assert not self.decider.shouldChangeStateInformation("Fail",1)

    def testShouldChangeStateForFailedWithTwoExpected(self):
        assert not self.decider.shouldChangeStateInformation("Fail",2)

    def testAddedAndTwoDrivesExpected(self):
        assert not self.decider.isThisAnError("SpareActive", 2)

    def testAddedAndOneDriveExpected(self):
        assert not self.decider.isThisAnError("SpareActive",1)

    def testFailedAndTwoDrivesExpected(self):
        assert self.decider.isThisAnError("Fail",2)

    def testFailedAndOneDrivesExpected(self):
        assert not self.decider.isThisAnError("Fail",1)

if __name__ == '__main__':
    unittest.main()

