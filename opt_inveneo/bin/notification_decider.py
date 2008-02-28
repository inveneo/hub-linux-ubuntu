

class NotificationDecider:
    def isThisAnError(self,message,numDrives):
        if message == "Added":
            return False
        else:
            return numDrives == 2

    def shouldChangeStateInformation(self,message,numDrives):
        return message == "Added" and numDrives == 1
