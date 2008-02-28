#!/usr/bin/env python

class NotificationDecider:
    def isThisAnError(self,message,numDrives):
        if (message == "SpareActive" or message == "RebuildFinished"):
            return False
        else:
            return (message == "Fail" or message == "DegradedArray") and numDrives == 2

    def shouldChangeStateInformation(self,message,numDrives):
        return (message == "SpareActive" or message == "RebuildFinished") and numDrives == 1
