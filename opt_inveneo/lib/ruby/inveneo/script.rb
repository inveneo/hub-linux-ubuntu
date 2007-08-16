require 'English' # 'english' aliases for $ variables, e.g. $? becomes $CHILD_STATUS
require 'inveneo'
require 'pathname'

MAX_APT_PACAKGES=20

module Inveneo::Script
  def self.log_error(mess) 
    self.log_message(mess, STDERR)
  end
   

  def self.log_message(mess, console=STDERR) 
    begin
      console.puts(mess)
      File.open(::INV_LOG, "a") { |log|
        log.puts(mess)
      }
    rescue => ex
      console.puts("Couldn't open log file: #{ex}")
      # could open log file
    end
  end
    
    def self.set_boot_flag(flag)
       fail "Could not set flag \"#{flag}\": #{$?}" unless system("touch #{::INV_BOOT_FLAG_DIR}/#{flag}") 
    end
    
    def self.clear_boot_flag(flag)
        fail "Could not clear flag \"#{flag}\": #{$?}" unless system("rm #{::INV_BOOT_FLAG_DIR}/#{flag}")
    end

    # synFileName: full path to a synaptics 'saved markings' file
    # simulate: construct apt-get simulation command?
    # purge: issue removes as purges? NOTE: system ignores Synpatics purge flags always
    # return: an array of apt-get commands or nil
    # exceptions: lets any file expections propagate
    def self.synaptic_to_apt(synFileName, simulate=false, sudo=false, purge=true)
        installs=[]
        removes=[]
        matcher=/^(\S+)\s+(\S+)$/

        File.open(synFileName,"r") { |synFile| 
            synFile.each { |line|
                next if line=~ /^\s*\#/ # skip comments
                match=matcher.match(line)
                next if match.nil? || match.length != 3

                case match[2]
                when "install"
                    installs << match[1]
                when "deinstall"
                    removes << match[1]
                end
            }
        }

        commands=[]

        unless (removes.length == 0)
            remove_cmd_base=  (sudo ? "sudo " : "")+
                "apt-get -y --force-yes "+
                (simulate ? "-s " : "")+
                (purge ? "--purge " : "")+
                "remove "
            num_packages=0
            remove_cmd =  nil
            removes.each { |e|
                remove_cmd = remove_cmd_base if remove_cmd.nil?
		        remove_cmd += "#{e} "
		        num_packages += 1
                if (num_packages==MAX_APT_PACAKGES) then
	                commands << remove_cmd
                    num_packages = 0
                    remove_cmd = nil
                end
            }
            commands << remove_cmd unless remove_cmd.nil?
        end

        unless (installs.length == 0)
            install_cmd_base= (sudo ? "sudo " : "")+
            "apt-get -y --force-yes "+
            (simulate ? "-s " : "")+
            "install "
            num_packages=0
	    install_cmd=nil
            installs.each { |e|
                install_cmd = install_cmd_base if install_cmd.nil?
                install_cmd += "#{e} "
                num_packages += 1
                if (num_packages==MAX_APT_PACAKGES) then
                    commands << install_cmd
                    num_packages = 0
                    install_cmd=nil
                end
            }
            commands << install_cmd unless install_cmd.nil?
        end
        
 #       unless (installs.length == 0)
 #           installs.each { |e| 
 #               install_cmd =
 #               (sudo ? "sudo " : "")+
 #               "apt-get -y --force-yes "+
 #               (simulate ? "-s " : "")+
 #               "install "+e
 #               commands << install_cmd
 #           }
 #       end

        commands.length == 0 ? nil : commands
    end
end
