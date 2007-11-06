require 'socket'

class ConfigurationController < ApplicationController
  @@BAD_FILE_TYPE="400 Bad Request--config file type or name invalid"
  @@NOT_FOUND="404 Not Found"

  # Constants
  @@SHARED_STATION_CONFIG_FILE=Pathname.new("#{RAILS_ROOT}/saved-configuration/station/station-shared.tar.gz")
  @@SHARED_STATION_INITIAL_CONFIG_FILE=Pathname.new("#{RAILS_ROOT}/saved-configuration/station/initial-config-shared.conf")
  @@USER_CONFIG_PATH=Pathname.new("#{RAILS_ROOT}/saved-configuration/user")

  @@SERVER_VERSION="1.0.0"
  
  @@cleanup_thread=nil
  @@cleanup_thread_mutex=Mutex.new
  
  before_filter :start_clean_config_thread

  def ConfigurationController.get_server_version
    @@SERVER_VERSION
  end

  def hostname_for_mac(mac)
      # TODO: read hostname prefix value from server settings
      "station-#{mac}"
  end
  
  def version
    respond_to do |format| 
      format.html  { render :action => 'version' }
      format.xml { render :xml => "<configuration-server><version>#{@@SERVER_VERSION}</version></configuration-server>" } 
      format.text { render :text => @@SERVER_VERSION } 
    end 
  end

  def get_user_config
    # to be safe, we get a read lock, copy the file to /tmp, release the lock, use send_file to send it
    # it's a little ugly, but the actual data isn't sent until this method returns so there is no 
    # clean way to bracket the sending of the data with a block.
    
    # TODO: Implement a 'clean-up' routine to sweep out tmp regularly!

    # see if we have an :id
    # TODO: Set-up restricted request routing so Rails enforces id
    if params[:id].blank?
      logger.error("Need a valid user name.")
      render :nothing=>true, :status=>@@BAD_FILE_TYPE
      return
    end

    user=params[:id]

    local_config_file=@@USER_CONFIG_PATH+(user+".tar.gz")

    if !local_config_file.exist?
      logger.warn("No config file found: #{local_config_file}")
      render :nothing=>true, :status=>@@NOT_FOUND
      return
    end

    temp_file=tmpFilename()

    File.open(local_config_file.to_s()+".lock", "a+") { |lock|
      lock.flock(File::LOCK_EX)
      FileUtils.copy(local_config_file, temp_file)
      lock.flock(File::LOCK_UN)
    }

    send_file(temp_file, :stream=>true)

    # NOTE: Can't erase temp_file, it's not sent yet! Needs to be a cleanup routine

  end

  def get_station_config
    # to be safe, we get a read lock, copy the file to /tmp, release the lock, use send_file to send it
    # it's a little ugly, but the actual data isn't sent until this method returns so there is no 
    # clean way to bracket the sending of the data with a block.
    
    # TODO: Implement a 'clean-up' routine to sweep out tmp regularly!

    # see if we have an :id
    # TODO: Set-up restricted request routing so Rails enforces id
    if params[:id].blank? || params[:id] !~ %r{^[a-f0-9]{12}$}
      logger.error("Need a valid station MAC address.")
      render :nothing=>true, :status=>@@BAD_FILE_TYPE
      return
    end

    # station=params[:id]

    local_config_file=@@SHARED_STATION_CONFIG_FILE

    if !local_config_file.exist?
      logger.warn("No config file found: #{local_config_file}")
      render :nothing=>true, :status=>@@NOT_FOUND
      return
    end

   temp_file=tmpFilename()
   
   File.open(local_config_file.to_s()+".lock", "a+") { |lock|
     lock.flock(File::LOCK_EX)
     FileUtils.copy(local_config_file, temp_file)
     lock.flock(File::LOCK_UN)
   }
    
    send_file(temp_file, :stream=>true)

    # NOTE: Can't erase temp_file, it's not sent yet! Needs to be a cleanup routine    
  end
  
  def get_station_initial_config
    # see if we have an :id
    # TODO: Set-up restricted request routing so Rails enforces id
    if params[:id].blank? || params[:id] !~ %r{^[a-f0-9]{12}$}
      logger.error("Need a valid station MAC address.")
      render :nothing=>true, :status=>@@BAD_FILE_TYPE
      return
    end
    
    station=params[:id]
    
    config=InitialConfig.getDefaultConfig() # creates if doesn't exist
    
    if config.nil?
      logger.info("Staton Inital Config requested for #{station} and none available")
      render :nothing=>true, :status=>@@NOT_FOUND
      return
    end
    
    temp_file=tmpFilename()
    
    File.open(temp_file, "w") { |tf|
      tf.puts %[# Initial Configuration\n\n]
      tf.puts %[INV_CONFIG_HOST="#{Socket.gethostname}"\n]
      tf.puts %[INV_CONFIG_HOST_TYPE="hub"\n]
      tf.puts %[INV_HOSTNAME="#{hostname_for_mac(station)}"\n]
      for attr in config.attribute_names().collect { |el| el.to_sym }
        logger.debug("Found attr: #{attr}\n")
        next if attr == :hostname # skip because set manually above
        tf.puts %[#{CONFIG_ATTR_TO_BASH[attr]}="#{config[attr]}"\n] unless CONFIG_ATTR_TO_BASH[attr].blank?
      end
    }

    logger.debug("Config file contents:\n"+File.open(temp_file, "r") { |f| f.readlines.join })
    send_file(temp_file, :stream=>true)
    
    # NOTE: Can't erase temp_file, it's not sent yet! Needs to be a cleanup routine    
  end
  
  def save_user_config
    # TODO: refactor this and sace station below as they are almost identical
    
    # see if we have an :id
    # TODO: Set-up restricted request routing so Rails enforces id
    if params[:id].blank?
      logger.error("Need a valid user name.")
      render :nothing=>true, :status=>@@BAD_FILE_TYPE
      return
    end
    
    user=params[:id].strip
    config_file=params['config_file']
    
    if config_file.nil?
      logger.error("No config file found")
      render :nothing=>true, :status=>@@BAD_FILE_TYPE
      return
    end
    
    # convert to basename in case browser sends full client-side path
    basename=Pathname.new(config_file.original_filename).basename.to_s.strip
    content_type=config_file.content_type().strip # for some reason this has a ^M on the end!
    
    logger.info("Username: #{user}")
    logger.info("File basename: #{basename}")
    logger.info("Content type: #{content_type}")
    
    # check file type
    if content_type != "application/octet-stream"
      logger.error("#{@@BAD_FILE_TYPE}: #{basename}, #{content_type}")
      render :nothing=>true, :status=>@@BAD_FILE_TYPE
      return
    end
    
    local_config_file=@@USER_CONFIG_PATH+(user+".tar.gz")
    
    File.open(local_config_file.to_s()+".lock", "a+") { |lock|
      lock.flock(File::LOCK_EX)
      save_posted_file(config_file, local_config_file)
      lock.flock(File::LOCK_UN)
    }
    
    render :nothing=>true
  end

  def save_station_config
    config_file=params['config_file']
    
    if config_file.nil?
      logger.error("No config file found")
      render :nothing=>true, :status=>@@BAD_FILE_TYPE
      return
    end
    
    # convert to basename in case browser sends full client-side path
    basename=Pathname.new(config_file.original_filename).basename.to_s.strip
    content_type=config_file.content_type().strip # for some reason this has a ^M on the end!

    logger.info("File basename: #{basename}")
    logger.info("Content type: #{content_type}")
    
    # check file type
    if content_type != "application/octet-stream" || basename != "station.tar.gz"
      logger.error("#{@@BAD_FILE_TYPE}: #{basename}, #{content_type}")
      render :nothing=>true, :status=>@@BAD_FILE_TYPE
      return
    end
    
    # For now we only save ONE machine config and it overrides all others
    # so first thing is to make sure there are no locks present which 
    # would indicate that someone else is reading or writing the image file
    
    File.open(@@SHARED_STATION_CONFIG_FILE.to_s()+".lock", "a+") { |lock|
      lock.flock(File::LOCK_EX)
      save_posted_file(config_file, @@SHARED_STATION_CONFIG_FILE)
      lock.flock(File::LOCK_UN)
    }
   
    render :nothing=>true
  end

  # Map for config values
  CONFIG_BASH_TO_ATTR={ "INV_TIME_ZONE" => :timezone,
    "INV_NTP_ON" => :ntp_on,
    "INV_NTP_SERVERS" => :ntp_servers,
    "INV_PROXY_ON" => :proxy_on,
    "INV_HTTP_PROXY" => :http_proxy,
    "INV_HTTP_PROXY_PORT" => :http_proxy_port,
    "INV_HTTPS_PROXY" => :https_proxy,
    "INV_HTTPS_PROXY_PORT" => :https_proxy_port,
    "INV_FTP_PROXY" => :ftp_proxy,
    "INV_FTP_PROXY_PORT" => :ftp_proxy_port,
    "INV_PHONE_HOME_ON" => :phone_home_on,
    "INV_PHONE_HOME_REG_URL" => :phone_home_reg,
    "INV_PHONE_HOME_CHECKIN_URL" => :phone_home_checkin,
    "INV_LOCALE" => :locale,
    "INV_SINGLE_USER_LOGIN" => :single_user_login
  }

  CONFIG_ATTR_TO_BASH=CONFIG_BASH_TO_ATTR.invert()
  
  def save_station_initial_config
    config_file=params['config_file']

    mac = params[:id]

    if config_file.nil?
      logger.error("No config file found")
      render :nothing=>true, :status=>@@BAD_FILE_TYPE
      return
    end

    if mac.blank?
      logger.error("Need a valid station mac address.")
      render :nothing=>true, :status=>@@BAD_FILE_TYPE
      return
    end

    # convert to basename in case browser sends full client-side path
    basename=Pathname.new(config_file.original_filename).basename.to_s.strip
    content_type=config_file.content_type().strip # for some reason this has a ^M on the end!

    logger.info("File basename: #{basename}")
    logger.info("Content type: #{content_type}")

    # check file type
    if content_type != "text/plain" || basename !="initial-config.conf"
      logger.error("#{@@BAD_FILE_TYPE}: #{basename}, #{content_type}")
      render :nothing=>true, :status=>@@BAD_FILE_TYPE
      return
    end
	
    # read file into a Hash
    # TODO: Move to a method or a converter class
    line_match=/^\s*([a-zA-Z0-9_]+)="\s*(.+?)\s*".*$/
    values= { :mac => params[:id] }
    config_file.each_line { |line|
      match=line_match.match(line)
      
      # continue if not valid line
      next if match.nil?
      
      logger.info("Found config value: #{match[1]} => #{match[2]}")
      
      # now set values
      key= CONFIG_BASH_TO_ATTR[match[1]]
      if key.blank? 
        logger.warn("Unrecognized config key: #{match[1]}")
        next
      end
      
      values[key]=match[2]
    }


    # Retrieve a record for the given mac
    config = InitialConfig.getConfigForMAC(values[:mac])
    config.attributes=values;
  
    logger.debug("Config to save:\n #{config.to_yaml()}")

    # save it
    config.save!()

    # Now save it to defaults
    config = InitialConfig.getDefaultConfig()
    values[:mac]=InitialConfig::DEFAULT_MAC
    config.attributes=values;
    
    config.save!()

    render :nothing=>true
  end

  private
  # wow this sucks, file may be one of TWO kinds of objects
  # so we have to save them differently
  def save_posted_file(src, dest)
    if src.local_path().blank?
      # copy bits from stream
      File.open(dest,"wb") {|file|
        file.write(src.read)
      }
    else
      # shortcut and just copy it from local file
      FileUtils.copy(src.local_path, dest)
    end
  end

  TMP_MAX_AGE=3600 # 1 hr
  def start_clean_config_thread
    logger.debug("Cleanup thread: #{@@cleanup_thread}")
    return unless @@cleanup_thread.nil?
    @@cleanup_thread_mutex.synchronize {
      if @@cleanup_thread.nil?
        logger.info("Starting clean-up thread")
        @@cleanup_thread=Thread.new {
          while true
            now=Time.now
            # find all files in tmp dir more than 1 hr old and erase them
            Dir.glob("#{tmpDir()}/#{TEMP_BASE_NAME}.*") { |fn|
              mod_time=File.mtime(fn)
              if ((now -  mod_time) > TMP_MAX_AGE)
                logger.debug("will remove old temp file: #{fn} last modified: #{mod_time}")
                File.delete(fn) 
              end
            }
            # sleep 2 hours
            sleep(7200) 
          end
        }
        logger.info(@@cleanup_thread.inspect)
      end
    }
  end
  
  # temp helpers
  # TO DO: True Ruby-ness would have this be a module mixin to TempFile or some crap
  
  TEMP_BASE_NAME="inv_temp"
  TEMP_DIR=(Pathname.new(RAILS_ROOT)+"tmp").expand_path.to_s
  def tmpFilename(basename=TEMP_BASE_NAME, dir=TEMP_DIR)
      tmp=Tempfile.new(basename, dir)
      temp_file=tmp.path
      tmp.close!
      temp_file
  end
  
  def tmpDir()
     TEMP_DIR 
  end
end