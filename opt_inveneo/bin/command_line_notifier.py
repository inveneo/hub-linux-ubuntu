#!/usr/bin/env python

import os

class CommandLineNotifier:
    def __init__(self, notifier_program):
        self.notifier_program = notifier_program

    def sendErrorNotification(self):
        os.system(self.notifier_program)
