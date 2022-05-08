require 'httparty'
require 'rspec'

Given(/^the service is healthy$/) do
  for attempt in 0..300
    begin
      @health = HTTParty.get("#{$app}/health")
      break if @health.code == 200
    rescue => error
      puts(error)
    end
    puts("Retrying health check.")
    sleep(1)
  end
  expect(@health.code).to eq(200)
end
