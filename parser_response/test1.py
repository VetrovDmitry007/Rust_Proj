from parser_response import ResponseParser
from typing import List

# response = b"HTTP/1.1 200 OK\r\nHost: example.com\r\nContent-Type: text/plain\r\nContent-Length: 12\r\n\r\nHello, world\n"
# response = b'HTTP/1.1 301 Moved Permanently\r\nConnection: keep-alive\r\nContent-Length: 162\r\nServer: GitHub.com\r\nContent-Type: text/html\r\nLocation: https://gunicorn.org/\r\nX-GitHub-Request-Id: 6642:9CFC:8BD6E9:8DF453:65622067\r\nAccept-Ranges: bytes\r\nDate: Sat, 25 Nov 2023 16:27:19 GMT\r\nVia: 1.1 varnish\r\nAge: 0\r\nX-Served-By: cache-fra-eddf8230071-FRA\r\nX-Cache: MISS\r\nX-Cache-Hits: 0\r\nX-Timer: S1700929639.243087,VS0,VE95\r\nVary: Accept-Encoding\r\nX-Fastly-Request-ID: a1ad7303c7f7029492e0f15b1a51d1c557942c39\r\n\r\n<html>\r\n<head><title>301 Moved Permanently</title></head>\r\n<body>\r\n<center><h1>301 Moved Permanently</h1></center>\r\n<hr><center>nginx</center>\r\n</body>\r\n</html>\r\n'

ls_response = [b'HTTP/1.1 301 Moved Permanently\r\nConnection: keep-alive\r\n',
               b'Content-Length: 162\r\nServer: GitHub.com\r\nContent-Type: text/html\r\nLocation:',
               b' https://gunicorn.org/\r\nX-GitHub-Request-Id: 6642:9CFC:8BD6E9:8DF453:65622067\r\n',
               b'Accept-Ranges: bytes\r\nDate: Sat, 25 Nov 2023 16:27:19 GMT\r\nVia: 1.1 varnish\r\nAge: ',
               b'0\r\nX-Served-By: cache-fra-eddf8230071-FRA\r\nX-Cache: MISS\r\nX-Cache-Hits: 0\r\nX-Timer: S1700929639.',
               b'243087,VS0,VE95\r\nVary: Accept-Encoding\r\nX-Fastly-Request-ID: a1ad7303c7f7029492e0',
               b'f15b1a51d1c557942c39\r\n\r\n<html>\r\n<head><title>301 Moved Permanently</title></head>\r\n',
               b'<body>\r\n<center><h1>301 Moved Permanently</h1></center>\r\n<hr><center>nginx</center>\r\n</body>\r\n</html>\r\n']

eof_mark = b"</html>\r\n"
# eof_mark = b""

response_body: List[bytes] = []
parser = ResponseParser()
while not parser.is_message_complete():
    response = ls_response.pop(0)
    parser.execute(response, eof_mark)
    # print(f'{parser.is_partial_body()=}')
    # print(parser.recv_body())
    print(f"{parser.is_headers_complete()=}")
    rec = parser.recv_body()
    if len(rec) > 0:
        response_body += [rec]

print(parser.get_status_code())
print(parser.get_headers())
print(f'{parser.is_message_complete()=}')
print(b"".join(response_body))

