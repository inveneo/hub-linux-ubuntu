class ConfigurationController < ApplicationController
  @@BAD_FILE_TYPE="400 Bad Request--config file type or name invalid"
  @@NOT_FOUND="404 Not Found"

  # Constants
  @@SHARED_STATION_CONFIG_FILE=Pathname.new("#{RAILS_ROOT}/saved-configuration/station/station-shared.tar.gz")
  @@SHARED_STATION_INITIAL_CONFIG_FILE=Pathname.new("#{RAILS_ROOT}/saved-configuration/station/initial-config-shared.conf")
  @@USER_CONFIG_PATH=Pathname.new("#{RAILS_ROOT}/saved-configuration/user")

  @@SERVER_VERSION="1.0.0"

  def ConfigurationController.get_server_version
    @@SERVER_VERSION
  end

  def host_name_for(mac)
      # TODO: read hostname prefix value
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

    # get a tempfile name, TODO: make this a mixin utility function on Tempfile
    tmp=Tempfile.new("tmp_config")
    temp_file=tmp.path
    tmp.close!

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

    # get a tempfile name, TODO: make this a mixin utility function on Tempfile
    tmp=Tempfile.new("tmp_config")
    temp_file=tmp.path
    tmp.close!
   
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

      # station=params[:id]

      local_config_file=@@SHARED_STATION_INITIAL_CONFIG_FILE

      if !local_config_file.exist?
        logger.warn("No config file found: #{local_config_file}")
        render :nothing=>true, :status=>@@NOT_FOUND
        return
      end

      # get a tempfile name, TODO: make this a mixin utility function on Tempfile
      tmp=Tempfile.new("tmp_config")
      temp_file=tmp.path
      tmp.close!

     File.open(local_config_file.to_s()+".lock", "a+") { |lock|
       lock.flock(File::LOCK_EX)
       FileUtils.copy(local_config_file, temp_file)
       lock.flock(File::LOCK_UN)
     }

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
  
  def save_station_initial_config
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
    if content_type != "text/plain" || basename !="initial-config.conf"
      logger.error("#{@@BAD_FILE_TYPE}: #{basename}, #{content_type}")
      render :nothing=>true, :status=>@@BAD_FILE_TYPE
      return
    end


    # For now we only save ONE machine config and it overrides all others
    # so first thing is to make sure there are no locks present which 
    # would indicate that someone else is reading or writing the image file
    
    File.open(@@SHARED_STATION_INITIAL_CONFIG_FILE.to_s()+".lock", "a+") { |lock|
      lock.flock(File::LOCK_EX)
      save_posted_file(config_file, @@SHARED_STATION_INITIAL_CONFIG_FILE)
      lock.flock(File::LOCK_UN)
    }
   
    render :nothing=>true
  end


  # Map for config values
  CONFIG_VALUES={ "INV_TIME_ZONE" => :timezone,
		  "INV_HOSTNAME" => :hostname,
		  "INV_NTP_ON" => :ntp_on,
		  "INV_NTP_SERVERS" => :ntp_servers,
		  "INV_PROXY_ON" => :proxy_on,
		  "INV_HTTP_PROXY" => :http_proxy,
		  "INV_HTTPS_PROXY" => :https_proxy,
		  "INV_FTP_PROXY" => :ftp_proxy,
		  "INV_PHONE_HOME_ON" => :phone_home_on,
		  "INV_PHONE_HOME_REG_URL" => :phone_home_reg,
		  "INV_PHONE_HOME_CHECKIN_URL" => :phone_home_checkin,
		  "INV_LOCALE" => :locale
		}

  def save_station_initial_config_db
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
    # TODO: Move into InitialCOnfig
    line_match=/^\s*([a-zA-Z0-9_]+)="\s*(.+?)\s*".*$/
    values= { :mac => params[:id] }
    config_file.each_line { |line|
      match=line_match.match(line)
      
      # continue if not valid line
      next if match.nil?
      
      logger.info("Found config value: #{match[1]} => #{match[2]}")
      
      # now set values
      key= CONFIG_VALUES[match[1]]
      if key.blank? 
        logger.warn("Unrecognized config key: #{match[1]}")
        next
      end
      
      values[key]=match[2]
    }


    # Try to retrieve a record for the given mac
    config = InitialConfig.find(:first, :conditions => [ "mac = ?", mac ]) 
    
    if config.nil?
      config=InitialConfig.new(values)
    else
      config.attributes=values;
    end
  
    logger.debug("Config to save:\n #{config.to_yaml()}")

    # save it
    config.save!()

    # Now save it to defaults
    values[:mac]=InitialConfig::DEFAULT_MAC

    config = InitialConfig.find(:first, :conditions => [ "mac = ?", InitialConfig::DEFAULT_MAC ]) 
    
    if config.nil?
      config=InitialConfig.new(values)
    else
      config.attributes=values;
    end
    
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
end
