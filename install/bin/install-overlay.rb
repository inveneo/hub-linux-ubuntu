#!/usr/bin/ruby -I/opt/inveneo/lib/ruby

require 'inveneo/script'
require 'fileutils'
require 'pathname'
require 'tempfile'

def fix_perms(opt)
end

def fix_owners(opt)
    # global switch back to root
    FileUtils.chown_R('root', 'root', (opt+"install/overlay"))

    # NOTE: Fix any one-off's that are owned by a special user like CUPS or AVAHI
    # fix any special owners
    FileUtils.chown_R('cupsys', 'lp', (opt+"install/overlay/etc/cups"))
    FileUtils.chmod(3755, (opt+"install/overlay/etc/cups"))
end

def pre_overlay_transfer(overlay_root, dest)
end

def post_overlay_transfer(overlay_root, dest)
end

def transfer_overlay(src, dest)
    # run cpio pass-through to copy everything
    # do it in a block so that Dir will restore cwd 
    # automagically.
    Dir.chdir(src.to_s) { |new_dir|
        system("find . -name .svn -prune -o -print0 | cpio --null -pvud #{dest}")
    }
end

def make_links(dest)
end


if $0 == __FILE__
    root = Pathname.new(File.dirname(File.expand_path($0))).parent
    opt = root.parent
    overlay_root = opt+"install/overlay"
    puts("opt: "+opt)

    if ! overlay_root.exist?
        STDERR.puts("Can not find subdir 'overlay'")
        exit 1
    end

    puts("\nFixing permissions in #{opt} ...\n")
    fix_perms(opt)

    puts("\nFixing owernship in #{opt} ...\n")
    fix_owners(opt)
    
    dest=Pathname.new("/")
    puts("\nRunning pre-transfer processing...\n")
    pre_overlay_transfer(overlay_root, dest)
    
    puts("\nTransfering overlay files to root (/)\n")
    transfer_overlay(overlay_root, dest)
    
    puts("\nSetting up any required symlinks...\n")
    make_links(dest)
    
    puts("\nRunning post-transfer processing...\n")
    post_overlay_transfer(overlay_root, dest)

    exit 0
end
