#!/usr/bin/ruby -I/opt/inveneo/lib/ruby

require 'inveneo/script'
require 'fileutils'
require 'pathname'
require 'pp'

def issue_apt_commands(cmd_array) 
    cmd_array.each { |c|
        puts("Issuing command:\n#{c}\n")
        system(c)
        puts("\n\n")
    }
end

if $0 == __FILE__
    unless ARGV.length == 1
        puts ("Usage: xubuntu-to-inveneo.rb <package list directory> | <markings file>")
        exit 1
    end

    package_dir = Pathname.new(ARGV[0])

    if ! ( package_dir.exist? && package_dir.readable? )
        STDERR.puts("Can't read pacakge directory/file: #{package_dir}")
        exit 2
    end

    #
    # Copy sources.list to /etc (if found)
    #
    puts("\nUpdating sources lists...\n")
    apt_conf=Pathname.new(package_dir+"apt")
    if (apt_conf.exist?)
        FileUtils.cp_r(apt_conf, "/etc/")
    end

    # set-up GPG keys
    puts("\nUpdating GPG keys...\n")
    system("wget http://medibuntu.sos-sts.com/repo/medibuntu-key.gpg -O- | apt-key add - ")
    system("wget http://community.inveneo.org/apt/inveneo.gpg -O- | apt-key add - ")
    
    puts("\nUpdating apt-cache...\n")
    system("/usr/bin/apt-get update")

    # If it's a dir, process each file found, otherwise process just the argument
    if (File.stat(package_dir).directory?)
        files=package_dir.entries
        files.sort!

        files.each { |file|
            # skip directories
            next if file.basename.to_s=="sources.list" || File.stat(package_dir+file).directory? 

            puts("Applying markings from \"#{file.basename}\"\n")
            issue_apt_commands(Inveneo::Script::synaptic_to_apt(package_dir+file))
        }
    elsif
        # just a single file  
        issue_apt_commands(Inveneo::Script::synaptic_to_apt(package_dir))
    end

    # run autcremove, upgrade, clean
    puts("\n\nRunning autoremove\n")
    system("/usr/bin/apt-get -y --force-yes --purge autoremove")

    puts("\n\nRunning upgrade\n")
    system("/usr/bin/apt-get -ym --force-yes dist-upgrade")

    puts("\n\nrunning clean\n")
    system("/usr/bin/apt-get -y --purge clean")

    exit 0
end
