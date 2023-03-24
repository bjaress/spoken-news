
Given(/^Wikipedia is available$/) do
  poll("wikipedia wiremock startup check/reset", 200) do
    HTTParty.post("#{$url[:wikipedia]}/__admin/reset").code
  end
end

Given(/^there is a headline about (.*)$/) do |topic|
  # Newest first
  @headlines = (@headlines || []).unshift(topic)
  headline_htmls = @headlines.map{|t| $NEWS[t][:headline]}

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
              :* => "<div><ul><li>#{headline_htmls.join('</li><li>')}</li></ul></div>"

  
            }
          }
        }
      }
    }.to_json
  })
  expect(response.code).to eq(201)
end

Then(/^news is retrieved from Wikipedia$/) do
  response = HTTParty.post("#{$url[:wikipedia]}/__admin/requests/find", {
    :body => {
      :method => "GET",
      :urlPath => "/w/api.php",
      :queryParameters => {
        :action => {:equalTo => "parse"},
        :format => {:equalTo => "json"},
        :prop => {:equalTo => "text"},
        :page => {:equalTo => "Template:In_the_news"},
        :section => {:equalTo => "0"}
      }
    }.to_json
  })
  requests = JSON.parse(response.body)["requests"]
  expect(requests).to have_attributes(length: 1)
end

