#based on:
# http://recipes.sinatrarb.com/p/testing/rspec

require 'rack/test'
require 'sinatra'
require 'rspec'
require 'capybara'
require 'capybara/dsl'
require 'capybara/rspec'

ENV['RACK_ENV'] = 'test'

require File.join(File.dirname(__FILE__), '.', 'test_server.rb')

module RSpecMixin
  include Rack::Test::Methods
  def app() Sinatra::Application end
end

Capybara.app = Sinatra::Application

Capybara.register_driver :selenium do |app|
  Capybara::Selenium::Driver.new(app, browser: :chrome)
end

Capybara.javascript_driver = :selenium

Capybara.configure do |config|
  config.default_max_wait_time = 30
  config.default_driver = :selenium
  config.wait_on_first_by_default = true
end

RSpec.configure do |config|
  config.include Capybara::DSL
  config.include RSpecMixin
end