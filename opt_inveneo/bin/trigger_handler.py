#!/usr/bin/env python

import sys
import os

sys.path.append(os.path.realpath('/opt/inveneo/bin'))
sys.path.append(os.path.realpath('/opt/inveneo/lib/python/inveneo'))

import degrade_actions

from notification_decider import *
from command_line_status_handler import *


class TriggerHandler:
    def __init__(self, handler, decider):
        self.handler = handler
        self.decider = decider

    def runMain(self, args):
        event_name = args[1]
        current_state = self.handler.getCurrentStatus()
        if self.decider.isThisAnError(event_name, current_state):
            degrade_actions.main()
        self.handler.updateCurrentStatus()

if __name__ == '__main__':
    TriggerHandler(CommandLineStatusHandler("/opt/inveneo/lib/python/inveneo/get_disk_status.py", "/opt/inveneo/lib/python/inveneo/update_disk_status.py"), NotificationDecider()).runMain(sys.argv)
