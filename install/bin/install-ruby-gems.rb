#!/usr/bin/ruby -I/opt/inveneo/lib/ruby

require 'fileutils'
require 'pathname'
require 'tempfile'



# Ruby Gem packages--noted here for completeness, but currently installed manually
# GEMS, install directly from source! 
# rails manual dependcies: rake, sqlite3-ruby
# rails auto-installed dependencies:  activesupport, activerecord, actionpack, actionmailer, actionwebservice
# rails
# mongrel auto-installed dependencies: fastthread, cgi_multipart_eof_fix
# mongrel
# mongrel_cluster


def install_gems(file)


end


if $0 == __FILE__
    unless ARGV.length == 1
        puts ("Usage: install-rub-gems.rb <gem list>")
        exit 1
    end
    
    begin
        IO.foreach(ARGV[0]) { |line|
            next if line =~ /^\s*#/ # skip comment lines
            
            match=/^\s*(\S+)\s+(install|deinstall)\s*(?:#.*)?$/.match(line)
            
            next if match.nil? # no match
            
            case match[2]
            when "install"
                %x[gem install #{match[1]} --no-rdoc --no-test --include-dependencies]
            when "deinstall"
                %x[gem install #{match[1]} --no-rdoc --no-test --include-dependencies]
            end
        }
    rescue
        puts("Error opening gem package list: #{ARGV[0]}")
        exit 1
    end

    exit 0
end
