require 'httparty'
require 'rspec'
require 'base64'

Given(/^the service is healthy$/) do
  poll("health check", 200) do
    HTTParty.get("#{$url[:app]}/health").code
  end
end

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
          :tts_server => $url[:google],
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
