class CreateInitialConfigs < ActiveRecord::Migration
  def self.up
    # sessions
    create_table :sessions do |t|
      t.column :session_id, :string
      t.column :data, :text
      t.column :updated_at, :datetime
    end

    add_index :sessions, :session_id
    add_index :sessions, :updated_at

    # users
    create_table "users", :force => true do |t|
      t.column :login,                     :string
      t.column :email,                     :string
      t.column :crypted_password,          :string, :limit => 40
      t.column :salt,                      :string, :limit => 40
      t.column :created_at,                :datetime
      t.column :updated_at,                :datetime
      t.column :remember_token,            :string
      t.column :remember_token_expires_at, :datetime
    end

    # initial configs
    create_table :initial_configs do |t|
      t.column :mac,		:string,	{:null=>false, :unique=>true }
      t.column :timezone,	:string
      t.column :ntp_on,	:boolean, 	{:null=>false , :default => true }
      t.column :ntp_servers,	:string, 	{:null=>false}
      t.column :proxy_on,	:boolean, 	{:null=>false, :default => false }
      t.column :http_proxy,	:string
      t.column :http_proxy_port,	:int, {:null=>false, :default => 8080 }
      t.column :https_proxy,	:string
      t.column :https_proxy_port,	:int, {:null=>false, :default => 8080 }
      t.column :ftp_proxy,	:string
      t.column :ftp_proxy_port,	:int, {:null=>false, :default => 8080 }
      t.column :phone_home_on,	:boolean, 	{:null=>false, :default => true}
      t.column :phone_home_reg, :string
      t.column :phone_home_checkin, :string
      t.column :locale,	:string,	{:null=>false }
      t.column :single_user_login, :boolean, {:null => false, :default => true }
      t.primary_key :mac
    end
  end
  
  def self.down
    drop_table :initial_configs
    drop_table "users"
    drop_table :sessions
  end
end
