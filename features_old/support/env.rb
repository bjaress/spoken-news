require 'httparty'
require 'date'

$showId = 1234

# Use start of given day as a reference point for mocks and test assertions.
$today = Date.parse(ENV['TODAY'])

class UrlLookup
  def [](key)
    # Expect environment variable with .url at end of name
    ENV["#{key}.url"]
  end
end
$url = UrlLookup.new

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
    sleep(0.1 * 2**([attempt, 12].min))
  end
  puts("Done trying #{description}.")
  STDOUT.flush
end
