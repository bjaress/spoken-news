require 'httparty'
require 'rspec'

When(/^the scheduled time arrives$/) do
  # https://cloud.google.com/pubsub/docs/push#receive_push
  response = HTTParty.post($url[:app], {
    :headers => {'content-type': 'application/json'},
    :body => {
      :message => {
        :attributes => {
          :spreaker_url => $url[:spreaker],
          :spreaker_token => "DUMMY_TOKEN",
          :spreaker_show_id => $showId,
          :tts_api_key => "DUMMY_KEY",
          :tts_server => $url[:google]
        },
        :messageId => "blahblah"
      },
      :subscription => "blah/blah/blah"
    }.to_json
  })
  expect(response.code).to eq(200)
end

Then(/^audio is generated from text$/) do
  #https://cloud.google.com/text-to-speech/docs/basics
  response = HTTParty.post("#{$url[:google]}/__admin/requests/find", {
    :body => {
      :method => "POST",
      :urlPath => "/v1/text:synthesize"
    }.to_json
  })

  requests = JSON.parse(response.body)["requests"]
  expect(requests).to have_attributes(length: 1)
end

Then(/^an audio file is uploaded to Spreaker$/) do
  #https://developers.spreaker.com/api/
  #https://wiremock.org/docs/api/#tag/Requests/paths/~1__admin~1requests~1find/post
  response = HTTParty.post("#{$url[:spreaker]}/__admin/requests/find", {
    :body => {
      :method => "POST",
      :urlPath => "/v2/shows/#{$showId}/episodes"
    }.to_json
  })

  upload_request = JSON.parse(response.body)["requests"][0]
  headers = upload_request["headers"]
  expect(headers["Authorization"]).to eq("Bearer DUMMY_TOKEN")

  content_type = headers["Content-Type"]
  # There's extra stuff in the content-type to specify the boundary
  # between parts.
  expect(content_type).to include("multipart/form-data")

  # Parser can't han't handle actual mp3 data
  # https://stackoverflow.com/a/73551605
  # http://www.w3.org/TR/html401/interact/forms.html#h-17.13.4
  #parsed = parse_multipart_form(content_type, upload_request["body"])
  #expect(parsed.params).to have_key("title")
  #expect(parsed.params["media_file"][:filename]).to eq("audio.mp3")
  #expect(parsed.params["media_file"][:type]).to eq("audio/mp3")
end
