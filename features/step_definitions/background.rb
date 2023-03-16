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

Given(/^Wikipedia is available$/) do
  poll("wikipedia wiremock startup check/reset", 200) do
    HTTParty.post("#{$url[:wikipedia]}/__admin/reset").code
  end
  response = HTTParty.post("#{$url[:wikipedia]}/__admin/mappings", {
    :body => {
      :request => {
        :urlPath => "/w/api.php",
        :queryParameters => {
          :page => {:equalTo => "Template:In_the_news"}
        }
      },
      :response => {
        :status => 200,
        :jsonBody => {
          :parse =>  {
            :title =>  "Template:In the news",
            :pageid =>  482256,
            :text =>  {
              :* =>  "<div><ul><li>An <a href=\"/wiki/Thing\">event</a> occurred.</li></ul></div>"
            }
          }
        }
      }
    }.to_json
  })
  expect(response.code).to eq(201)
end

Given(/^Spreaker API is available$/) do
  poll("spreaker wiremock startup check/reset", 200) do
    HTTParty.post("#{$url[:spreaker]}/__admin/reset").code
  end
  #https://developers.spreaker.com/api/
  response = HTTParty.post("#{$url[:spreaker]}/__admin/mappings", {
    :body => {
      :request => {
        :urlPath => "/v2/shows/#{$showId}/episodes"
      },
      :response => {
        :status => 200
      }
    }.to_json
  })
  expect(response.code).to eq(201)
end

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
