#!/usr/bin/ruby -I/opt/inveneo/lib/ruby

require 'inveneo/script'
require 'fileutils'
require 'pathname'

if $0 == __FILE__
    root = Pathname.new(File.dirname(File.expand_path($0))).parent
    overlay_root = root+"overlay"

    if ! overlay_root.exist?
        STDERR.puts("Can not find subdir 'overlay'")
        exit 1
    end

    puts("\nInstalling apt packages...\n")
    system("#{root+'bin/xubuntu-to-inveneo.rb'} #{root+'package.d'}")

    puts("\nInstalling Ruby Gems...\n")
    system("#{root+'bin/install-ruby-gems.rb'} #{root+'gems'}")
   
    puts("\nInstalling overlay...\n")
    system("#{root+'bin/install-overlay.rb'}")  
    
    exit 0
end
