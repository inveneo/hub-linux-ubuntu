class InitialConfig < ActiveRecord::Base
  DEFAULT_MAC="deaddeadbeef"
  
  DEFAULT_ATTRS={
    :mac => DEFAULT_MAC,
    :timezone => "America/Los_Angeles",
    :ntp_on => true,
    :ntp_servers => "hub.local:pool.ntp.org",
    :proxy_on => false,
    :http_proxy => "http://hub.local:8080",
    :https_proxy => "",
    :ftp_proxy => "http://hub.local:8080",
    :phone_home_on => true,
    :phone_home_reg => "http://community.inveneo.org/phonehome/reg",
    :phone_home_checkin => "http://community.inveneo.org/phonehome/checkin",
    :locale => "en_UK.utf8",
    :single_user_login => true
  }

  @@url_regex = /(?#WebOrIP)((?#protocol)((http|https):\/\/)?(((?#domain)[a-zA-Z0-9\-]+(?#TLD)(\.[a-zA-Z]+){1,2})|(?#IPAddress)((25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9])\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[0-9])))+(?#Port)(:[1-9][0-9]*)?)+(?#Path)((\/((?#dirOrFileName)[a-zA-Z0-9_\-\%\~\+]+)?)*)?(?#extension)(\.([a-zA-Z0-9_]+))?(?#parameters)(\?([a-zA-Z0-9_\-]+\=[a-z-A-Z0-9_\-\%\~\+]+)?(?#additionalParameters)(\&([a-zA-Z0-9_\-]+\=[a-z-A-Z0-9_\-\%\~\+]+)?)*)?/
  
  @@locale_regex=/^[a-z][a-z](_[A-Z][A-Z](.[uU][tT][fF]8)?)?$/
  @@mac_regex=/^[a-z0-9]{12,12}/

  # Class helpers creation methods
  
  # return: the config instance. Will return new with default values if doesn't
  #         yet exist
  def InitialConfig.getConfigForMAC(mac, createIfNotFound=true)
    config=InitialConfig.find(:first, :conditions => [ "mac = ?", mac ]) 
    if config.nil? && createIfNotFound
      InitialConfig.new( { :mac => mac} ) 
    else
      config
    end
  end

  # return: the existing default (if exists) or a newly created one if not
  def InitialConfig.getDefaultConfig(createIfNotFound=true)
    config=InitialConfig.find(:first, :conditions => [ "mac = ?", InitialConfig::DEFAULT_MAC ]) 
    if config.nil? && createIfNotFound
      InitialConfig.new( { :mac => InitialConfig::DEFAULT_MAC } )
    else
      config
    end
  end

  # Initializer
  def initialize(*args)
    # merge args with defaults
    argHash=nil
    if args && args.length()>0 && args[0].kind_of?(Hash)
      argHash=DEFAULT_ATTRS.merge(args[0])
    else
      argHash=DEFAULT_ATTRS
    end
    
    # call super to be fully created
    super(argHash) 
  end


  # Validation
  validates_presence_of :timezone
  validates_format_of :mac, :with=> @@mac_regex, :message => "MAC address must be 12 hex values, all lowercase, no separator"
  validates_format_of :locale, :with => @@locale_regex, :message => "Must be a valid locale string. E.g. en_UK.utf8"
  validates_inclusion_of :ntp_on, :proxy_on, :phone_home_on, :single_user_login, :in => [true, false] 

  protected
  def validate
    for uri in [ :phone_home_checkin, :phone_home_reg, :http_proxy, :https_proxy, :ftp_proxy ]
      errors.add(uri, "must be empty or a valid url") unless self[uri].blank? || self[uri] =~ @@url_regex
    end
    
    errors.add(:http_proxy, "Http_proxy must be valid when Proxy is turned on") if proxy_on && http_proxy.blank?
    errors.add(:ntp_servers, "Must have a valid NTP server host or IP if NTP is on") if ntp_on && ntp_servers.blank?
    for uri in [ :phone_home_reg, :phone_home_checkin ]
      errors.add(uri, %{If phone home is on "Phone Home Reg" and "Phone Home Checkin" must be valid}) if phone_home_on && self[uri].blank?
    end
  end	
	
end

