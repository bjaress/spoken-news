require 'httparty'
require 'rspec'

When(/^a message is posted$/) do
  @response = HTTParty.get($app)
end

Then(/^the process runs$/) do
  expect(@response.code).to eq(200)
end
