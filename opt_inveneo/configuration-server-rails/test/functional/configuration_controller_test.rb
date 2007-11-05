require File.dirname(__FILE__) + '/../test_helper'
require 'configuration_controller'

# Re-raise errors caught by the controller.
class ConfigurationController; def rescue_action(e) raise e end; end

class ConfigurationControllerTest < Test::Unit::TestCase
  def setup
    @controller = ConfigurationController.new
    @request    = ActionController::TestRequest.new
    @response   = ActionController::TestResponse.new
  end

  # Replace this with your real tests.
  def test_truth
    assert true
  end
end
