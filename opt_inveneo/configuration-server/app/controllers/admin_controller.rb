class AdminController < ApplicationController
  def index
    render :action => 'dashboard'
  end

  def all
    list
    render :action => 'list'
  end

  # GETs should be safe (see http://www.w3.org/2001/tag/doc/whenToUseGet.html)
  verify :method => :post, :only => [ :destroy, :create, :update ],
         :redirect_to => { :action => :list }

  def list
    @initial_config_pages, @initial_configs = paginate :initial_configs, :per_page => 10
  end

  def show
    @initial_config = InitialConfig.find(params[:id])
  end

  def new
    @initial_config = InitialConfig.new
  end

  def create
    @initial_config = InitialConfig.new(params[:initial_config])
    if @initial_config.save
      flash[:notice] = 'InitialConfig was successfully created.'
      redirect_to :action => 'list'
    else
      render :action => 'new'
    end
  end

  def edit_default_config
      config=InitialConfig.find(:first, :conditions => ["mac = ?", InitialConfig::DEFAULT_MAC])
      config=InitialConfig.new if config.nil?
      render :action => 'edit', :id=>InitialConfig::DEFAULT_MAC
  end

  def edit
    if params[:id] =~ /^[a-f0-9]{12,12}$/
      @initial_config = InitialConfig.find(:first, :conditions => ["mac = ?", params[:id]])
    else
      @initial_config = InitialConfig.find(params[:id])
    end
  end

  def update
    @initial_config = InitialConfig.find(params[:id])
    if @initial_config.update_attributes(params[:initial_config])
      flash[:notice] = 'InitialConfig was successfully updated.'
      redirect_to :action => 'show', :id => @initial_config
    else
      render :action => 'edit'
    end
  end

  def destroy
    InitialConfig.find(params[:id]).destroy
    redirect_to :action => 'list'
  end

  STATION_CONFIG_DIR="#{RAILS_ROOT}/saved-configuration/station"
  USER_CONFIG_DIR="#{RAILS_ROOT}/saved-configuration/user"
  CONFIG_MATCH=/^(.+)\.tar\.gz$/
  BLANK_CONFIG_FILE="#{RAILS_ROOT}/saved-configuration/blank.tar.gz"

  def reset_config
    # reset initial config
    config = InitialConfig.getDefaultConfig()
    config.set_to_default_values()
    config.save!()

    # set machine and user config tar balls to blanks
    for dirname in [ STATION_CONFIG_DIR, USER_CONFIG_DIR ]
      Dir.chdir(dirname) {
        Pathname.new(dirname).each_entry { |e|
          next unless e.file? && (CONFIG_MATCH =~ e.basename) != nil
          logger.debug("In reset config resetting entry: #{e}")
          FileUtils.copy(BLANK_CONFIG_FILE, e)
        }
      }
      end
    redirect_to :action => 'list'
  end
end
