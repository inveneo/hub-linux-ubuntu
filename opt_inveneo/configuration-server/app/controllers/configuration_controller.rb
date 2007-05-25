class ConfigurationController < ApplicationController
  @@BAD_FILE_TYPE="400 Bad Request--config file type invalid"
  @@NOT_FOUND="404 Not Found"

  # Constants
  @@SHARED_STATION_CONFIG_FILE=Pathname.new("#{RAILS_ROOT}/saved-configuration/station/station-shared.tar.gz")
  @@SHARED_STATION_CONFIG_LOCKS_PATH=Pathname.new("#{RAILS_ROOT}/saved-configuration/station/station.locks")
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

    lock_path=@@USER_CONFIG_PATH+(user+".locks")
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

    Inveneo::FileLock.get_read_lock(lock_path) {
      FileUtils.copy(local_config_file, temp_file)
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

    lock_path=@@SHARED_STATION_CONFIG_LOCKS_PATH
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

    Inveneo::FileLock.get_read_lock(lock_path) {
      FileUtils.copy(local_config_file, temp_file)
    }
    
    #
    # add etc/hostname to the arhive--it means unzipping, adding, rezipping
    #
    
    # 1. generate hostname file
    %x{mkdir -p #{temp_file}.dir}
  
    # 2. unzip and add to archive
    temp_dir="#{temp_file}.dir"
    %x{tar -C #{temp_dir} -xvzf #{temp_file}}
    %x{mkdir -p #{temp_dir}/etc}
    %x{echo "#{host_name_for(params[:id])}" > #{temp_dir}/etc/hostname}
    
    # 3. tar it back into place
    puts temp_dir
    Dir.chdir(temp_dir) {
        %x{touch GOT_HERE}
        %x{tar -cvzf #{temp_file} *}
    }
    
    # 4. Clean up
    #%x{rm -rf #{temp_file}.dir #{temp_file}.tar}

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
    
    lock_path=@@USER_CONFIG_PATH+(user+".locks")
    local_config_file=@@USER_CONFIG_PATH+(user+".tar.gz")
    Inveneo::FileLock.get_write_lock(lock_path) {
      save_posted_file(config_file, local_config_file)
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
    if content_type != "application/octet-stream" || basename !~ %r{^station-[a-f0-9]{12}\.tar\.gz$}
      logger.error("#{@@BAD_FILE_TYPE}: #{basename}, #{content_type}")
      render :nothing=>true, :status=>@@BAD_FILE_TYPE
      return
    end
    
    # For now we only save ONE machine config and it overrides all others
    # so first thing is to make sure there are no locks present which 
    # would indicate that someone else is reading or writing the image file
    Inveneo::FileLock.get_write_lock(@@SHARED_STATION_CONFIG_LOCKS_PATH) {
      save_posted_file(config_file, @@SHARED_STATION_CONFIG_FILE)
    }
   
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
