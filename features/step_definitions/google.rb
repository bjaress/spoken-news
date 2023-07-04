require 'httparty'
require 'rspec'

Given(/^Google text-to-speech API is available$/) do
  poll("google wiremock startup check/reset", 200) do
    HTTParty.post("#{$url[:google]}/__admin/reset").code
  end
  # Ruby Rack parser can't han't handle actual mp3 data
  # This is the base64 encoding of "foo"
  @mp3base64 = "Zm9v"
  #https://cloud.google.com/text-to-speech/docs/basics
  response = HTTParty.post("#{$url[:google]}/__admin/mappings", {
    :body => {
      :request => {
        :urlPath => "/v1/text:synthesize"
      },
      :response => {
        :status => 200,
        :jsonBody => {
          :audioContent => @mp3base64
        }
      }
    }.to_json
  })
  expect(response.code).to eq(201)
end


Then(/^audio is generated about (.*)$/) do |topic|
  #https://cloud.google.com/text-to-speech/docs/basics
  response = HTTParty.post("#{$url[:google]}/__admin/requests/find", {
    :body => {
      :method => "POST",
      :urlPath => "/v1/text:synthesize"
    }.to_json
  })

  requests = JSON.parse(response.body)["requests"]
  expect(requests).to have_attributes(length: 1)
  request = requests[0]

  expect(request["url"]).to include("key=DUMMY_KEY")
  body = JSON.parse(request["body"])
  expect(body["input"]["text"]).to eq($NEWS[topic][:episode_contents])
  expect(body["voice"]).to have_key("languageCode")
  expect(body["voice"]).to have_key("name")
  expect(body["audioConfig"]).to include("audioEncoding" => "MP3")
  expect(body["audioConfig"]).to have_key("speakingRate")
  expect(body["audioConfig"]).to have_key("pitch")
end
