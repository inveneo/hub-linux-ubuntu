import sys
import os

class CommandLineStatusHandler:
    def __init__(self,status_program,update_program):
        self.status_program = status_program
        self.update_program = update_program

    def getCurrentStatus(self):
        fp = os.popen(self.status_program)
        out = fp.read()
        fp.close()
        return int(out)

    def updateCurrentStatus(self):
        os.system(self.update_program)
