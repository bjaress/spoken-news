$showId = 1234

class UrlLookup
  def [](key)
    # Expect environment variable with .url at end of name
    ENV["#{key}.url"]
  end
end
$url = UrlLookup.new
