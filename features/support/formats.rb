require "rack"


# https://stackoverflow.com/a/73551605

def parse_multipart_form(content_type, multipart_form_data)
sanitized_multipart_form_data = multipart_form_data.gsub(/\r?\n/, "\r\n")

io = StringIO.new(sanitized_multipart_form_data)
tempfile = Rack::Multipart::Parser::TEMPFILE_FACTORY
bufsize = Rack::Multipart::Parser::BUFSIZE
query_parser = Rack::Utils.default_query_parser
Rack::Multipart::Parser.parse(
    io, sanitized_multipart_form_data.length,
    content_type, tempfile, bufsize, query_parser)
end
