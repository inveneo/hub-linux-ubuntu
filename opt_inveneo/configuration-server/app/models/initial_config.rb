class InitialConfig < ActiveRecord::Base
	@url_regex = /(?#WebOrIP)((?#protocol)((http|https):\/\/)?(?#subDomain)(([a-zA-Z0-9]+\.(?#domain)[a-zA-Z0-9\-]+(?#TLD)(\.[a-zA-Z]+){1,2})|(?#IPAddress)((25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9])\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[0-9])))+(?#Port)(:[1-9][0-9]*)?)+(?#Path)((\/((?#dirOrFileName)[a-zA-Z0-9_\-\%\~\+]+)?)*)?(?#extension)(\.([a-zA-Z0-9_]+))?(?#parameters)(\?([a-zA-Z0-9_\-]+\=[a-z-A-Z0-9_\-\%\~\+]+)?(?#additionalParameters)(\&([a-zA-Z0-9_\-]+\=[a-z-A-Z0-9_\-\%\~\+]+)?)*)?/
	
	@locale_regex=/^[a-z][a-z](?:_[A-Z][A-Z](?:\.[uU][tT][fF]8)?)?$/
	
	validates_presence_of :timezone, :hostname_prefix, :default, :mac
	validates_format_of :locale, :with => @locale_regex, :message => "Must be a valid locale string. E.g. en_UK.utf8"
	validates_inclusion_of :ntp_on, :proxy_on, :phone_home_on, :in => [true, false] 

	def validate
		# TO DO: add validation of URLs and locale		
	end	
	
end

