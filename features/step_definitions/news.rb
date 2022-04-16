require 'httparty'
require 'rspec'

#TODO poll on healthcheck and dependencies before expecting app to work

When(/^a message is posted$/) do
  @response = HTTParty.post($app, {})
end

Then(/^the process runs$/) do
  expect(@response.code).to eq(200)
end
