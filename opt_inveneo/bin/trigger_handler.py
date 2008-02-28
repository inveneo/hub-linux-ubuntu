#!/usr/bin/env python

import sys

from notification_decider import *
from command_line_notifier import *
from command_line_status_handler import *


class TriggerHandler:
    def __init__(self, notifier, handler, decider):
        self.notifier = notifier
        self.handler = handler
        self.decider = decider

    def runMain(self, args):
        event_name = args[1]
        current_state = self.handler.getCurrentStatus()
        if self.decider.isThisAnError(event_name, current_state):
            self.notifier.sendErrorNotification()
        if self.decider.shouldChangeStateInformation(event_name, current_state):
            self.handler.updateCurrentStatus()

if __name__ == '__main__':
    TriggerHandler(CommandLineNotifier('/opt/inveneo/lib/python/inveneo/degrade_actions.py'), CommandLineStatusHandler("/opt/inveneo/lib/python/inveneo/get_disk_status.py", "/opt/inveneo/lib/python/inveneo/update_disk_status.py"), NotificationDecider()).runMain(sys.argv)
