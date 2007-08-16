#!/usr/bin/ruby -I/opt/inveneo/lib/ruby

require 'inveneo/script'
require 'fileutils'
require 'pathname'
require 'tempfile'

if $0 == __FILE__
  root = Pathname.new(File.dirname(File.expand_path($0))).parent
  opt = root.parent
  overlay_root = opt+"install/overlay"
  
  install_path=Pathname.new("/opt/install")
  inveneo_path=Pathname.new("/opt/inveneo")
  
  puts("\nUpdating /opt/inveneo\n")
  system("svn update #{inveneo_path}")
  
  puts("\nUpdating /opt/install\n")
  system("svn update #{install_path}")
  
  puts("\nAdding packages\n")
  system("#{root+"bin/xubuntu-to-inveneo.rb"} #{root+"package.d/02Adds"}")

  puts("\nInstalling Ruby Gems...\n")
  system("#{root+bin/install-ruby-gems.rb'} #{root+'gems-adds'}")
  
  puts("\nReinstalling overlay\n")
  system("#{root+"bin/install-overlay.rb"}")
  
  puts("\nDone. Press enter/return key to reboot...\n")
  STDIN.getc
  system("reboot")

  exit 0
end
