#
# Helpful utility methods
#
require 'inveneo/unicode'
require 'ipaddr'
require 'scanf'

module Inveneo
  module Utils
    def Utils.blank?(arg)
      !Utils.meaningful?(arg)
    end

    def self.meaningful?(arg)
      if arg.nil? 
        false
      elsif arg.kind_of?(String) 
        arg.strip.jlength>0
      else # to do fill in meaningful tests for other types
        false
      end
    end
  end

  #
  # Types
  #
    class User
        # class methods
        def self.current_user() 
            User.new(ENV['USER'])
        end
        
        def self.uid_for_username(uname)
          uid=*%x{/usr/bin/id -u #{uname}}.scanf('%d')
          uid.nil? ? -1 : uid
        end

        def self.username_for_uid(uid)
           %{getent passwd | awk -F ":" ' $3 == "1000" { print $1 }'}
        end
      
        def self.gid_for_username(uname)
            gid=*%x{/usr/bin/id -g #{uname}}.scanf('%d')
            gid.nil? ? -1 : gid
        end
        
        def self.home_for_username(uname)
            %x{echo ~#{uname}}.strip
        end

        attr_reader(:username, :uid, :gid, :home)

        def initialize(nameOrId)
            case nameOrId
            when String
                @username = nameOrId
                @uid = User.uid_for_username(@username)
            when Integer
                @uid = nameOrId
                @username = User.username_for_uid(@uid)
            else
                fail "usage: User.new(<username: String> | <uid: Intger>)"
            end
            
            fail "username or id invalid" if @uid==-1 || @username.nil?
            @home=User.home_for_username(@username)
            @gid=User.gid_for_username(@username)
        end
    end
  
  class DriveInfo
    attr_reader(:root_partition, :root_drive)

    def initialize()
        # get output of 'df', find drive mounted on '/' and parse
        root_part = %x[rdev | awk -F '/' '{ print "/"$(NF-2)"/"$(NF-1) }']
        fail "rdev failed to get root partition: #{root_part}" if !Inveneo::Utils.meaningful?(root_part)
        @root_partition=root_part.strip()
        
        # now get just the drive
        matched=@root_partition.match(/^(.+)[0-9]+$/)
        fail("Can't match drive part of: #{@root_partition}") if matched.nil?
        
        @root_drive=matched[1]
    end
  end # Class DriveInfo
  
  class MACAddr
    attr_accessor(:address)
    
    def initialize(inAddr, delim=':')
      @address = case inAddr
                 when MACAddr: inAddr.address
                 when Array: arrayToAddr(inAddr)
                 when String: stringToAddr(inAddr,delim)
                 else fail(ArgumentError, \
                           "Input must be String or an Array of Strings or Integers")
                 end
    end
    
    #
    # Conversions
    #
    def to_s(delim=':')
      str = @address.collect { |el| sprintf("%02x",el)+delim}.to_s.downcase
      
      # remove last delim
      str[0..-(delim.length+1)]
    end
    
    #
    # returns on integer by repeatedly left shifting the terms and
    # adding the next. Essentially the same as turning into a string,
    # removing the separator, and converting to an int. Eg. "aa:ff" becomes int(aaff)
    #
    def to_i
      @address.inject(0) { |sum, el| (sum << 8) + el }
    end
    
    #
    # Private constructor helpers
    #
    private
    def arrayToAddr(inAddr) 
      fail(ArgumentError, "Array must have 6 elements") if !inAddr || inAddr.length != 6
      inAddr.collect { |el|
        val = -1
        if el.kind_of?(String) && el.downcase=~/[0-9a-f]{2,2}/ then 
          val=el.hex()
        elsif el.kind_of?(Integer) then 
          val=el
        end
        
        fail(ArgumentError, "MAC Address elements must be between 0-255/00-ff") if !(0..255) === val
        val
      }
    end
    
    def stringToAddr(inAddr, delim) 
      fail(ArgumentError, "inAddr must be a non-nil, non-zero length string") if !Inveneo::Utils.meaningful?(inAddr)
      scanner = Regexp.new("\\#{delim}?([0-9a-f]{2,2})\\#{delim}?")
      arrayToAddr(inAddr.downcase.scan(scanner).flatten())
    end
  end # class MACAddr
  
  class NetAdapter
    #
    # Regexs to use to piece apart ifconfig output
    # NOTE: platfrom specific
    #
    @@match_adapter = Regexp.new(/^(.+?)\s.+HWaddr\s(.+?)\s/m)
    @@match_ipaddr = Regexp.new(/inet\saddr:([\d.]+)\s/m)
    @@match_up = Regexp.new(/.+UP.+Metric/m)
    @@gateway_match_str = "^0\\.0\\.0\\.0\\s+((?:\\d{1,3}[.]){3,3}\\d{1,3}).*ADAPT_NAME$"
    
    #
    # Class methods
    #

    #
    # Returns an array of _real_ network interfaces, by which I mean
    # devices with a HWAddr (not loopback, not sit etc...)
    #
    # If none found, returns nil
    #
    # NOTE: This is platform specific as it parses output of Linux 'ifconfig'
    # 
    def self.getInterfaces(no_loopback=true)
      ifaces = `ifconfig -a`
      fail(RuntimeError, "Cannot find 'ifconfig'") if !Inveneo::Utils.meaningful?(ifaces)
      self.extractNetAdapters(ifaces)
    end
    
    private
    def self.extractNetAdapters(ifaces)
      return nil if !Inveneo::Utils.meaningful?(ifaces)

      # Split into individual cards
      ifaces = ifaces.split(/\n\n/m) # now ifaces is an array of strings, one per card

      # build and return array of NetAdapters
      adapters = ifaces.collect { | str | 
        next if ! (matched = str.match(@@match_adapter)) # not a 'real' adapter
        name = matched[1]
        hwAddr = matched[2]
        
        matched = str.match(@@match_ipaddr)
        ipAddr = matched ? matched[1] : nil
        isUp = !(str =~ @@match_up).nil?
        
        NetAdapter.new(name, hwAddr, ipAddr, nil, isUp) # add gateway later
      }
      
      # clear out nils 
      # TODO: do this in one iterator walk?
      adapters = adapters.reject { | el | el == nil }
      adapters = nil if adapters.length==0 # turn empty array into nil

      addGateways(adapters) # add gateway info
    end

    def self.addGateways(adapters)
      return nil if adapters.nil?
      
      routes=`/sbin/route -n`
      if Inveneo::Utils.meaningful?(routes) then
        adapters.each { | adap |
          matcher = Regexp.new(@@gateway_match_str.sub(/ADAPT_NAME/, adap.dev_id), Regexp::MULTILINE)
          match = matcher.match(routes)
          adap.gateway = match.nil? ? nil : match[1]
        }
      end
      adapters
    end

    #
    # Instance methods
    #
    public
    attr_reader(:dev_id, :mac, :ip, :gateway, :is_up) 
    
    def initialize(inDevId, inMac, inIP, inGW, inIsUp)      
      @dev_id=inDevId
      @mac=MACAddr.new(inMac)
      @ip= inIP.nil? ? nil : IPAddr.new(inIP) # IP may be blank
      @gateway = inGW
      @is_up = (inIsUp == true) # force into boolean 
    end

    # separate writer because this is filled in after initialization... a hack...
    def gateway=(inGW)
        @gateway = inGW.nil? ? nil : IPAddr.new(inGW) # GW may be blank
    end

    def up?
      @is_up
    end

    def to_s 
      up = @is_up ? 'yes' : 'no'
      ip = @ip ? @ip : 'none'
      gw = @gateway ? @gateway : 'none'
      "name: #{@dev_id}\nmac: #{@mac}\nip: #{ip}\ngateway: #{gw}\nup: #{up}\n\n"
    end
  end # class NetAdapter

  #
  # System Info, class only, don't instantiate
  #
  class SystemInfo
    def self.hostname
      hostname=`hostname`
      Inveneo::Utils.meaningful?(hostname) ? hostname.strip : ""
    end

    def self.hardware_id
      faces = NetAdapter.getInterfaces();
      faces.nil? ? -1 : faces[0].mac.to_i
    end
    
    def self.drive_info
       return DriveInfo.new 
    end

    # return array of ints so that '2.0.2' becomes [2,0,2]
    # returns empty array if no version found
    # NOTE: IGNORES NON NUMERIC DIGITS so 2.0.2a becomes [2,0,2] !!
    def self.os_version
      version_file = nil
      version_array = []
      begin
        version_file = File.open(INV_OS_VERSION_FILE, 'r')
        version_str = version_file.readline # will raise exception if no line
        version_str.scan(/(\d+)[.]?/) { | term | version_array << term[0].to_i}
      rescue => ex
        STDERR.puts ex # error to the terminal
        version_array = [] # version not found
      ensure
        version_file.close unless version_file.nil?
      end
      version_array # return array
    end

    #
    # TODO: Hub handling... have to decide what to do here...
    #
    
    def self.net_adapters
      Inveneo::NetAdapter.getInterfaces()
    end
    
    def self.primary_nic
        Inveneo::NetAdapter.getInterfaces()[0]
    end

    private
    def initialize
      fail "Class object only. Do not instantiate"
    end
  end
end

if $0 == __FILE__


end
