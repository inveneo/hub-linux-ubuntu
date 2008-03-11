""" This module tests the functionality in the notification_decider that is the part
of the Inveneo system that makes sure we only send notifications in the right sitations"""

import sys
import os
import unittest

sys.path.append(os.path.realpath('.'))

import trigger_handler

class TestTriggerHandler(unittest.TestCase):
    def setUp(self):
        self.triggerHandler = TriggerHandler(mock_notifier, mock_state_updater, mock_notification_decider)

    def testTriggerHandlerShouldNotifyWhenFailedDriveWithTwoDrivesExpected(self):
        assert self.triggerHandler.runMain(arguments
