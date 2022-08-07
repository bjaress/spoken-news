require 'httparty'
require 'rspec'

When(/^the scheduled time arrives$/) do
  response = HTTParty.post($app, {
    :body => {
      :storage => $storage
    }.to_json
  })
  expect(response.code).to eq(200)
end


Then(/^the old refresh token is retrieved$/) do
  # https://cloud.google.com/storage/docs/json_api
  # https://wiremock.org/docs/api/#tag/Requests/paths/~1__admin~1requests~1find/post
  response = HTTParty.post("#{$storage}/__admin/requests/find", {
    :body => {
      :urlPathPattern => '.*'
    }.to_json
  })
  matchingRequests = JSON.parse(response.body)['requests']
  puts(matchingRequests)
  expect(matchingRequests).to_not be_empty
end
