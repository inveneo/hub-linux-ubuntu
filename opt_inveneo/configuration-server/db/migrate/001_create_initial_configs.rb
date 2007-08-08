class CreateInitialConfigs < ActiveRecord::Migration
  def self.up
    create_table :initial_configs do |t|
	t.column :mac,		:string,	{:default => "default", :null=>false, :unique=>true }
	t.column :timezone,	:string, 	{:default => "America/Los_Angeles"}
	t.column :hostname,	:string
	t.column :hostname_prefix,	:string, 	{:default => "inveneo-cs-"}
	t.column :ntp_on,	:boolean, 	{:default => false, :null=>false}
	t.column :ntp_servers,	:string, 	{:default => "pool.ntp.org", :null=>false}
	t.column :proxy_on,	:boolean, 	{:default => false, :null=>false }
	t.column :http_proxy,	:string,	{:default => "192.168.100.1:8080"}
	t.column :https_proxy,	:string,	{:default => nil}
	t.column :ftp_proxy,	:string,	{:default => "192.168.100.1:8080"}
	t.column :phone_home_on,	:boolean, 	{:default => true, :null=>false}
	t.column :phone_home_reg, :string,	{:default => "http://community.inveneo.org/phone-home2/register"}
	t.column :phone_home_checkin, :string,	{:default => "http://community.inveneo.org/phone-home2/checkin"}
	t.column :locale,	:string,	{:default => "en_US.utf8", :null=>false }

	t.primary_key :mac
    end
  end

  def self.down
    drop_table :initial_configs
  end
end
