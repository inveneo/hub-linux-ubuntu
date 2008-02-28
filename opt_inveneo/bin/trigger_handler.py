import sys

import notification_decider
import command_line_notifier
import command_line_status_handler


class TriggerHandler:
    def __init__(self, notifier, handler, decider):
        self.notifier = notifier
        self.handler = handler
        self.decider = decider

    def runMain(self, args):
        pass

if __name__ == '__main__':
    TriggerHandler(CommandLineNotifier('/opt/inveneo/bin/error_notifier.py'), CommandLineStatusHandler("/opt/inveneo/bin/get_disk_status.py", "/opt/inveneo/bin/update_disk_status.py"), NotificationDecider()).runMain(sys.argv)
