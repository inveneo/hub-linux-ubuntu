require 'pathname'

module Inveneo

  class FileLock
    
    def FileLock.get_write_lock path
      if block_given?
        lock=FileLock.new(path, :write)
        yield
        lock.release
      end
    end

    def FileLock.get_read_lock path
      if block_given?
        lock=FileLock.new(path, :read)
        yield
        lock.release
      end
    end

    # instance
    def initialize(path, type)
      case type
      when :write
        @lock_file=acquire_write_lock(path)
      else :read
        @lock_file=acquire_read_lock(path)
      end
    end

    def release
      @lock_file.close!() unless @lock_file.nil?
    end

    def acquire_write_lock(path)
      lock_dir=Pathname.new(path)
      lock_dir.mkpath

      # semantics are simple, if no other files are in lock_dir, we write ours, otherwise we wait
      sleep 0.1 until Dir.glob(lock_dir+"*").length==0 

      # TODO: this isn't 100% atomic, another lock _could_ slip in between the sleep on the create...
      @lock_file=Tempfile.new("write_lock", lock_dir)
    end

    def acquire_read_lock(path)
      lock_dir=Pathname.new(path)
      lock_dir.mkpath

      # read locks are a little more complicated. Can grab one as long as no write lock
      sleep 0.1 until Dir.glob(lock_dir+"write_lock.*").length==0

      # TODO: this isn't 100% atomic, another lock _could_ slip in between the sleep on the create...
      @lock_file=Tempfile.new("read_lock", lock_dir)
    end
  end
end
