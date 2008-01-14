# tried to put this method into helpers.py and import it
# does not work though -- rjocham 
#import configurationserver.lib.helpers as h
import os
import glob

def empty_tmp_folder():
    count = 0
    for file in glob.glob('tmp/*'):
        try:
            os.remove(file) 
            count += 1
        except OSError:
            print 'Could not remove', file
    print "File(s) removed: ", count

print "Cleaning out tmp folder"
empty_tmp_folder()
print "Successfuly emptied tmp folder"
