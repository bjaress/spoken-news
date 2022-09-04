require 'httparty'
require 'rspec'

When(/^the scheduled time arrives$/) do
  response = HTTParty.post($url[:app], {
    :headers => {'content-type': 'application/json'},
    :body => {
      :spreaker => {
        :url => $url[:spreaker],
        :token => "DUMMY_TOKEN",
        :show_id => $showId
      }
    }.to_json
  })
  expect(response.code).to eq(200)
end

Then(/^an audio file is uploaded to Spreaker$/) do
  #https://developers.spreaker.com/api/
  #https://wiremock.org/docs/api/#tag/Stub-Mappings/paths/~1__admin~1mappings/post
  response = HTTParty.post("#{$url[:spreaker]}/__admin/requests/find", {
    :body => {
      :method => "POST",
      :urlPath => "/v2/shows/#{$showId}/episodes"
    }.to_json
  })
  body = JSON.parse(response.body)
  expect(body["requests"].length).to eq(1)
end
