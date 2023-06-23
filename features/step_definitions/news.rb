require 'httparty'
require 'rspec'
require 'base64'

Given(/^the service is healthy$/) do
  poll("health check", 200) do
    HTTParty.get("#{$url[:app]}/health").code
  end
end

When(/^it is time to generate news$/) do
  # https://cloud.google.com/pubsub/docs/push#receive_push
  response = HTTParty.post($url[:app], {
    :headers => {'content-type': 'application/json'},
    :body => {
      :message => {
        :attributes => {
          :spreaker_url => $url[:spreaker],
          :spreaker_token => "DUMMY_TOKEN",
          :spreaker_show_id => $showId,
          :spreaker_title_limit => ENV["spreaker.title_limit"],
          :spreaker_age_limit => 30,
          :tts_api_key => "DUMMY_KEY",
          :tts_server => $url[:google],
          :tts_length_limit => 60,
          :tts_intro => "INTRO",
          :tts_outro => "OUTRO",
          :wikipedia_url => $url[:wikipedia],
          :wikipedia_headlines_page => "Template:In_the_news"
        },
        :messageId => "blahblah"
      },
      :subscription => "blah/blah/blah"
    }.to_json
  })
  expect(response.code).to eq(200)
end

When(/^it is time to clean up episodes older than (\d+) days$/) do |days|
  # https://cloud.google.com/pubsub/docs/push#receive_push
  response = HTTParty.post($url[:app] + "/cleanup", {
    :headers => {'content-type': 'application/json'},
    :body => {
      :message => {
        # spreaker only
        :attributes => {
          :url => $url[:spreaker],
          :token => "DUMMY_TOKEN",
          :show_id => $showId,
          :title_limit => ENV["spreaker.title_limit"],
          :age_limit => days.to_i,
        },
        :messageId => "blahblah"
      },
      :subscription => "blah/blah/blah"
    }.to_json
  })
  expect(response.code).to eq(200), response
end
