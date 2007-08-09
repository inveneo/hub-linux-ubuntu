class CreateInitialConfigs < ActiveRecord::Migration
  def self.up
    create_table :initial_configs do |t|
      t.column :mac,		:string,	{:null=>false, :unique=>true }
      t.column :timezone,	:string
      t.column :ntp_on,	:boolean, 	{:null=>false}
      t.column :ntp_servers,	:string, 	{:null=>false}
      t.column :proxy_on,	:boolean, 	{:null=>false }
      t.column :http_proxy,	:string
      t.column :https_proxy,	:string
      t.column :ftp_proxy,	:string
      t.column :phone_home_on,	:boolean, 	{:null=>false}
      t.column :phone_home_reg, :string
      t.column :phone_home_checkin, :string
      t.column :locale,	:string,	{:null=>false }
      
      t.primary_key :mac
    end
  end
  
  def self.down
    drop_table :initial_configs
  end
end
