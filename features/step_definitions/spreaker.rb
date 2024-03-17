require 'httparty'


Given(/^Spreaker API is available$/) do
  poll("spreaker wiremock startup check/reset", 200) do
    HTTParty.post("#{$url[:spreaker]}/__admin/reset").code
  end

  # https://developers.spreaker.com/api/episodes/#uploading-a-recorded-episode
  response = HTTParty.post("#{$url[:spreaker]}/__admin/mappings", {
    :body => {
      :request => {
        :urlPath => "/v2/shows/#{$showId}/episodes",
        :method => "POST"
      },
      :response => {
        :status => 200
      }
    }.to_json
  })
  expect(response.code).to eq(201)

  existing_episodes([], {})
end

Given(/^there is an episode about (.*)$/) do |topic|
  @episode_topics = (@episode_topics || []).append(topic)
  @episode_dates = @episode_dates || {}
  @episode_dates[topic] = $today
  existing_episodes(@episode_topics, @episode_dates)
end

Given(/^there is a (\d+) day old episode about (.*)$/) do |days, topic|
  @episode_topics = (@episode_topics || []).append(topic)
  @episode_dates = @episode_dates || {}
  @episode_dates[topic] = $today - days.to_i
  existing_episodes(@episode_topics, @episode_dates)
end

def existing_episodes(topics, dates)
  episodes = topics.map{|t| {
    title: $NEWS[t][:episode_title],
    published_at: "#{dates[t]} 00:00:00",
    episode_id: $NEWS[t][:episode_id],
  }}

  # https://developers.spreaker.com/api/episodes/#retrieving-a-shows-episodes
  response = HTTParty.post("#{$url[:spreaker]}/__admin/mappings", {
    :body => {
      :request => {
        :urlPath => "/v2/shows/#{$showId}/episodes",
        :method => "GET"
      },
      :response => {
        :status => 200,
        :jsonBody => {
          :response => { :items => episodes }
        }
      }
    }.to_json
  })
  expect(response.code).to eq(201)
end

Then(/^the list of past episodes is retrieved from Spreaker$/) do
  response = HTTParty.post("#{$url[:spreaker]}/__admin/requests/find", {
    :body => {
      :method => "GET",
      :urlPath => "/v2/shows/#{$showId}/episodes",
      :queryParameters => {
        :filter => {:equalTo => "editable"},
        :sorting => {:equalTo => "oldest"}
      }
    }.to_json
  })
  requests = JSON.parse(response.body)["requests"]
  expect(requests.length).to be(1), "Requests for past espisodes: #{requests}"
  expect(requests[0]['headers']["Authorization"]).to eq("Bearer DUMMY_TOKEN")
end

Then(/^the audio file is uploaded to Spreaker$/) do
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

  # https://stackoverflow.com/a/73551605
  # http://www.w3.org/TR/html401/interact/forms.html#h-17.13.4
  parsed = parse_multipart_form(
    content_type, upload_request["body"].gsub(/\r?\n/, "\r\n"))
  expect(parsed.params).to have_key("title")
  expect(parsed.params["media_file"][:filename]).to eq("audio.mp3")
  expect(parsed.params["media_file"][:type]).to eq("audio/mp3")

  mp3data = parsed.params["media_file"][:tempfile].read
  mp3base64 = Base64.encode64(mp3data).strip
  expect(mp3base64).to eq(@mp3base64)

  @spreaker_params = parsed.params
end


Then(/^no audio file is uploaded to Spreaker$/) do
  response = HTTParty.post("#{$url[:spreaker]}/__admin/requests/find", {
    :body => {
      :method => "POST",
      :urlPath => "/v2/shows/#{$showId}/episodes"
    }.to_json
  })
  expect(JSON.parse(response.body)["requests"]).to eq([])
end


Then(/^the episode title is about (.*)$/) do |topic|
  expect(@spreaker_params["title"]).to eq($NEWS[topic][:episode_title])
end

Then(/^the episode description complies with Wikipedia's license$/) do
  expect(@spreaker_params["description"]).to include(
    "https://creativecommons.org/licenses/by-sa/4.0/")
end

Then(/^the episode description links to articles on (.*)$/) do |topic|
  $NEWS[topic][:articles].each do |title, body|
    oldid = body[:latest][:id]
    # permalink uses "oldid" for whatever ID was current at the time
    expect(@spreaker_params["description"]).to include(
      "#{$url[:wikipedia]}/w/index.php?title=#{title}&oldid=#{oldid}")
  end
end

# https://developers.spreaker.com/api/episodes/#deleting-an-episode
Then(/^the episode about (.*) is deleted$/) do |topic|
  response = HTTParty.post("#{$url[:spreaker]}/__admin/requests/find", {
    :body => {
      :method => "DELETE",
      :urlPath => "/v2/episodes/#{$NEWS[topic][:episode_id]}",
    }.to_json
  })
  requests = JSON.parse(response.body)["requests"]
  expect(requests.length).to be(1), "Deletes for espisode: #{requests}"
  expect(requests[0]['headers']["Authorization"]).to eq("Bearer DUMMY_TOKEN")
end

Then(/^the episode about (.*) is kept$/) do |topic|
  response = HTTParty.post("#{$url[:spreaker]}/__admin/requests/find", {
    :body => {
      :method => "DELETE",
      :urlPath => "/v2/episodes/#{$NEWS[topic][:episode_id]}",
    }.to_json
  })
  requests = JSON.parse(response.body)["requests"]
  expect(requests.length).to be(0), "Deletes for espisode: #{requests}"
end
