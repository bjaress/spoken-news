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
    HTTParty.get("#{$app}/health").code
  end
end

Given(/^there is an old refresh token stored$/) do
  poll("wiremock startup check", 200) do
    HTTParty.get("#{$storage}/__admin/mappings").code
  end
  # TODO mock refresh token
  # https://cloud.google.com/storage/docs/json_api
  # https://wiremock.org/docs/api/#tag/Stub-Mappings/paths/~1__admin~1mappings/post
  response = HTTParty.post("#{$storage}/__admin/mappings", {})
  expect(response.code).to eq(200)
end
