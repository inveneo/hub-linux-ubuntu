#
# General includes
#

# make sure unicode switch is on 
require 'inveneo/unicode' 

# load constants shared with shell scripts
module Inveneo
  SHARED_CONSTANTS="/opt/inveneo/lib/bash/constants.sh"
end

load Inveneo::SHARED_CONSTANTS

# bring in other files
require 'inveneo/string_tables'
require 'inveneo/utils'


