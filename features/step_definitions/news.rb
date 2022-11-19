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

  puts(upload_request)
  parsed = parse_multipart_form(content_type, upload_request["body"])
  puts(parsed)
  expect(parsed.params).to have_key("title")
  expect(parsed.params["media_file"][:filename]).to eq("audio.mp3")
  expect(parsed.params["media_file"][:type]).to eq("audio/mp3")

#  # http://www.w3.org/TR/html401/interact/forms.html#h-17.13.4
#  data = <<~DATA
#   Content-Type: multipart/form-data; boundary=AaB03x
#
#   --AaB03x
#   Content-Disposition: form-data; name="title"
#
#   Larry
#   --AaB03x
#   Content-Disposition: form-data; name="media_file"; filename="audio.mp3"
#   Content-Type: audio/mp3
#
#   ... contents of audio.mp3 ...
#   --AaB03x--
#  DATA
#
#  parsed = parse_multipart_form("multipart/form-data; boundary=AaB03x", data)
#  expect(parsed.params["title"]).to eq("Larry")
#  expect(parsed.params["media_file"][:filename]).to eq("audio.mp3")
#  expect(parsed.params["media_file"][:type]).to eq("audio/mp3")
end
