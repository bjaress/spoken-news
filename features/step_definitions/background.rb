require 'httparty'
require 'rspec'

def poll(description, target)
  for attempt in 0..300
    puts("Trying #{description}.")
    STDOUT.flush
    begin
      break if target == yield
      puts("Was not #{target}.")
      STDOUT.flush
    rescue => error
      puts(error)
    end
    sleep(1)
  end
  puts("Done trying #{description}.")
  STDOUT.flush
end

Given(/^the service is healthy$/) do
  poll("health check", 200) do
    HTTParty.get("#{$url[:app]}/health").code
  end
end

Given(/^Spreaker API is available$/) do
  poll("wiremock startup check/reset", 200) do
    HTTParty.post("#{$url[:storage]}/__admin/reset").code
  end
  #https://developers.spreaker.com/api/
  response = HTTParty.post("#{$url[:spreaker]}/__admin/mappings", {
    :body => {
      :request => {
        :urlPath => "/v2/shows/#{$showId}/episodes"},
      :response => {
        :status => 200
      }
    }.to_json
  })
  expect(response.code).to eq(201)
end
