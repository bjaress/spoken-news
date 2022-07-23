require 'httparty'
require 'rspec'

When(/^the scheduled time arrives$/) do
  response = HTTParty.post($app, {})
  expect(response.code).to eq(200)
end
