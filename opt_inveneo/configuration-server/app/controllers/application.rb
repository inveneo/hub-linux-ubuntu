# Filters added to this controller apply to all controllers in the application.
# Likewise, all the methods added will be available for all controllers.

class ApplicationController < ActionController::Base
  # Be sure to include AuthenticationSystem in Application Controller instead
  include AuthenticatedSystem

  # If you want "remember me" functionality, add this before_filter to Application Controller
  before_filter :login_from_cookie

  # Pick a unique cookie name to distinguish our session data from others'
  session :session_key => '_config-server_session_id'
end
