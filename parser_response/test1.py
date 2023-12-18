import base64
import collections
import json

from parser_response import ResponseParser
from typing import List

# http://192.168.133.223:8500/v1/health/service/mongo?passing=1

# response = b"HTTP/1.1 200 OK\r\nHost: example.com\r\nContent-Type: text/plain\r\nContent-Length: 12\r\n\r\nHello, world\n"
# response = b'HTTP/1.1 301 Moved Permanently\r\nConnection: keep-alive\r\nContent-Length: 162\r\nServer: GitHub.com\r\nContent-Type: text/html\r\nLocation: https://gunicorn.org/\r\nX-GitHub-Request-Id: 6642:9CFC:8BD6E9:8DF453:65622067\r\nAccept-Ranges: bytes\r\nDate: Sat, 25 Nov 2023 16:27:19 GMT\r\nVia: 1.1 varnish\r\nAge: 0\r\nX-Served-By: cache-fra-eddf8230071-FRA\r\nX-Cache: MISS\r\nX-Cache-Hits: 0\r\nX-Timer: S1700929639.243087,VS0,VE95\r\nVary: Accept-Encoding\r\nX-Fastly-Request-ID: a1ad7303c7f7029492e0f15b1a51d1c557942c39\r\n\r\n<html>\r\n<head><title>301 Moved Permanently</title></head>\r\n<body>\r\n<center><h1>301 Moved Permanently</h1></center>\r\n<hr><center>nginx</center>\r\n</body>\r\n</html>\r\n'

ls_response_1 = [b'HTTP/1.1 301 Moved Permanently\r\nConnection: keep-alive\r\n',
               b'Content-Length: 162\r\nServer: GitHub.com\r\nContent-Type: text/html\r\nLocation:',
               b' https://gunicorn.org/\r\nX-GitHub-Request-Id: 6642:9CFC:8BD6E9:8DF453:65622067\r\n',
               b'X-Consul-Index: 111\r\nAccept-Ranges: bytes\r\nDate: Sat, 25 Nov 2023 16:27:19 GMT\r\nVia: 1.1 varnish\r\nAge: ',
               b'0\r\nX-Served-By: cache-fra-eddf8230071-FRA\r\nX-Cache: MISS\r\nX-Cache-Hits: 0\r\nX-Timer: S1700929639.',
               b'243087,VS0,VE95\r\nVary: Accept-Encoding\r\nX-Fastly-Request-ID: a1ad7303c7f7029492e0',
               b'f15b1a51d1c557942c39\r\n\r\n<html>\r\n<head><title>301 Moved Permanently</title></head>\r\n',
               # b'<body>\r\n<center><h1>301 Moved Permanently</h1></center>\r\n<hr><center>nginx</center>\r\n</body>\r\n</html>\r\n']
               b'<body>\r\n<center><h1>301 Moved Permanently</h1></center>\r\n<hr><center>nginx</center>\r\n</body>\r\n</html>\r\n']

ls_response_2 = [b'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nVary: Accept-Encoding\r\nX-Consul-Default-Acl-Policy:',
                 b' allow\r\nX-Consul-Effective-Consistency: leader\r\nX-Consul-Index: 5100254\r\nX-Consul-Knownleader:',
                 b' true\r\nX-Consul-Lastcontact: 0\r\nX-Consul-Query-Backend: blocking-query\r\nDate: ',
                 b'Thu, 14 Dec 2023 16:15:07 GMT\r\nContent-Length: 1249\r\n\r\n[{"Node":{"ID":"570cfb54-d48b-09db-8fca-45570a8fb225",',
                 b'"Node":"sovadev3","Address":"192.168.133.223","Datacenter":"promavto","TaggedAddresses":{"lan":"192.168.133.223",',
                 b'"lan_ipv4":"192.168.133.223","wan":"192.168.133.223","wan_ipv4":"192.168.133.223"},"Meta":{"consul-network-segment":"",',
                 b'"consul-version":"1.16.2"},"CreateIndex":8,"ModifyIndex":4472626},"Service":{"ID":"mongo","Service":"mongo","Tags":[""],',
                 b'"Address":"","Meta":null,"Port":27017,"Weights":{"Passing":1,"Warning":1},"EnableTagOverride":false,"Proxy":',
                 b'{"Mode":"","MeshGateway":{},"Expose":{}},"Connect":{},"PeerName":"","CreateIndex":4472633,"ModifyIndex":4472633},',
                 b'"Checks":[{"Node":"sovadev3","CheckID":"serfHealth","Name":"Serf Health Status","Status":"passing","Notes":"",',
                 b'"Output":"Agent alive and reachable","ServiceID":"","ServiceName":"","ServiceTags":[],"Type":"","Interval":"",',
                 b'"Timeout":"","ExposedPort":0,"Definition":{},"CreateIndex":4472623,"ModifyIndex":4472623},{"Node":"sovadev3",',
                 b'"CheckID":"service:mongo","Name":"Service \'mongo\' check","Status":"passing","Notes":"","Output":"master",',
                 b'"ServiceID":"mongo","ServiceName":"mongo","ServiceTags":[""],"Type":"script","Interval":"10s","Timeout":"2s",',
                 b'"ExposedPort":0,"Definition":{},"CreateIndex":4472633,"ModifyIndex":5100254}]}]']

ls_response_3 = [b'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nVary:'
                 b' Accept-Encoding\r\nX-Consul-Default-Acl-Policy: allow\r\nX-Consul-Effective-Consistency:'
                 b' leader\r\nX-Consul-Index: 5098644\r\nX-Consul-Knownleader: true\r\nX-Consul-Lastcontact:'
                 b' 0\r\nX-Consul-Query-Backend: blocking-query\r\nDate: Thu, 14 Dec 2023 17:58:14 GMT\r\nContent-Length:'
                 b' 1266\r\n\r\n[{"Node":{"ID":"570cfb54-d48b-09db-8fca-45570a8fb225","Node":'
                 b'"sovadev3","Address":"192.168.133.223","Datacenter":"promavto","TaggedAddresses":'
                 b'{"lan":"192.168.133.223","lan_ipv4":"192.168.133.223","wan":"192.168.133.223","wan_ipv4":"192.168.133.223"},'
                 b'"Meta":{"consul-network-segment":"","consul-version":"1.16.2"},"CreateIndex":8,"ModifyIndex":4472626},'
                 b'"Service":{"ID":"postgres","Service":"postgres","Tags":[""],"Address":"","Meta":null,"Port":5432,'
                 b'"Weights":{"Passing":1,"Warning":1},"EnableTagOverride":false,"Proxy":'
                 b'{"Mode":"","MeshGateway":{},"Expose":{}},"Connect":{},"PeerName":"","CreateIndex":4472629,"ModifyIndex":4472629},'
                 b'"Checks":[{"Node":"sovadev3","CheckID":"serfHealth","Name":"Serf Health Status","Status":"passing",'
                 b'"Notes":"","Output":"Agent alive and reachable","ServiceID":"","ServiceName":"","ServiceTags":[],'
                 b'"Type":"","Interval":"","Timeout":"","ExposedPort":0,"Definition":{},"CreateIndex":4472623,"ModifyIndex":4472623},'
                 b'{"Node":"sovadev3","CheckID":"service:postgres","Name":"Service \'postgres\' check","Status":"passing",'
                 b'"Notes":"","Output":"Leader","ServiceID":"postgres","ServiceName":"postgres","ServiceTags":[""],'
                 b'"Type":"script","Interval":"10s","Timeout":"2s","ExposedPort":0,"Definition":{},"CreateIndex":4472629,'
                 b'"ModifyIndex":5098644}]}]']


ls_response_4 = [b'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nVary: Accept-Encoding\r\nX-Consul-Default-Acl-Policy:'
                 b' allow\r\nX-Consul-Effective-Consistency: leader\r\nX-Consul-Index: 5100678\r\nX-Consul-Knownleader:'
                 b' true\r\nX-Consul-Lastcontact: 0\r\nX-Consul-Query-Backend: blocking-query\r\nDate: Fri, 15 Dec 2023 08:'
                 b'32:57 GMT\r\nTransfer-Encoding: chunked\r\n\r\nd83\r\n[{"Node":{"ID":"570cfb54-d48b-09db-8fca-45570a8fb225",'
                 b'"Node":"sovadev3","Address":"192.168.133.223","Datacenter":"promavto","TaggedAddresses":{"lan":"192.168.133.223",'
                 b'"lan_ipv4":"192.168.133.223","wan":"192.168.133.223","wan_ipv4":"192.168.133.223"},"Meta":'
                 b'{"consul-network-segment":"","consul-version":"1.16.2"},"CreateIndex":8,"ModifyIndex":4472626},"Service":'
                 b'{"ID":"svc-6b484ced-b392-44dc-aaa4-5186bf5bfb7b","Service":"activator-default","Tags":'
                 b'["noc","svc-6b484ced-b392-44dc-aaa4-5186bf5bfb7b"],"Address":"192.168.133.223","TaggedAddresses":{"lan_ipv4":'
                 b'{"Address":"192.168.133.223","Port":39677},"wan_ipv4":{"Address":"192.168.133.223","Port":39677}},'
                 b'"Meta":null,"Port":39677,"Weights":{"Passing":1,"Warning":1},"EnableTagOverride":false,"Proxy":'
                 b'{"Mode":"","MeshGateway":{},"Expose":{}},"Connect":{},"PeerName":"","CreateIndex":5100618,"ModifyIndex":5100618},'
                 b'"Checks":[{"Node":"sovadev3","CheckID":"serfHealth","Name":"Serf Health Status","Status":"passing","Notes":"",'
                 b'"Output":"Agent alive and reachable","ServiceID":"","ServiceName":"","ServiceTags":[],"Type":"","Interval":"",'
                 b'"Timeout":"","ExposedPort":0,"Definition":{},"CreateIndex":4472623,"ModifyIndex":4472623},{"Node":"sovadev3",'
                 b'"CheckID":"service:svc-6b484ced-b392-44dc-aaa4-5186bf5bfb7b","Name":"Service \'activator-default\' check",'
                 b'"Status":"passing","Notes":"","Output":'
                 b'"HTTP GET http://192.168.133.223:39677/health/?service=svc-6b484ced-b392-44dc-aaa4-5186bf5bfb7b: 200 OK Output:'
                 b' OK","ServiceID":"svc-6b484ced-b392-44dc-aaa4-5186bf5bfb7b","ServiceName":"activator-default","ServiceTags":'
                 b'["noc","svc-6b484ced-b392-44dc-aaa4-5186bf5bfb7b"],"Type":"http","Interval":"10s","Timeout":"1s","ExposedPort":0,'
                 b'"Definition":{},"CreateIndex":5100618,"ModifyIndex":5100678}]},{"Node":{"ID":"570cfb54-d48b-09db-8fca-45570a8fb225",'
                 b'"Node":"sovadev3","Address":"192.168.133.223","Datacenter":"promavto","TaggedAddresses":{"lan":"192.168.133.223",'
                 b'"lan_ipv4":"192.168.133.223","wan":"192.168.133.223","wan_ipv4":"192.168.133.223"},"Meta":'
                 b'{"consul-network-segment":"","consul-version":"1.16.2"},"CreateIndex":8,"ModifyIndex":4472626},"Service":'
                 b'{"ID":"svc-a31a1c88-0633-4e1b-ab74-418e7b39c7cd","Service":"activator-default","Tags":'
                 b'["noc","svc-a31a1c88-0633-4e1b-ab74-418e7b39c7cd"],"Address":"192.168.133.223","TaggedAddresses":'
                 b'{"lan_ipv4":{"Address":"192.168.133.223","Port":20395},"wan_ipv4":{"Address":"192.168.133.223","Port":20395}},'
                 b'"Meta":null,"Port":20395,"Weights":{"Passing":1,"Warning":1},"EnableTagOverride":false,"Proxy":'
                 b'{"Mode":"","MeshGateway":{},"Expose":{}},"Connect":{},"PeerName":"","CreateIndex":5100630,"ModifyIndex":5100630},'
                 b'"Checks":[{"Node":"sovadev3","CheckID":"serfHealth","Name":"Serf Health Status","Status":"passing","Notes":"",'
                 b'"Output":"Agent alive and reachable","ServiceID":"","ServiceName":"","ServiceTags":[],"Type":"","Interval":"",'
                 b'"Timeout":"","ExposedPort":0,"Definition":{},"CreateIndex":4472623,"ModifyIndex":4472623},{"Node":"sovadev3",'
                 b'"CheckID":"service:svc-a31a1c88-0633-4e1b-ab74-418e7b39c7cd","Name":"Service \'activator-default\' check",'
                 b'"Status":"passing","Notes":"","Output":"HTTP GET http://192.168.133.223:20395/health/?service=svc-a31a1c88-0633-4e1b-ab74-418e7b39c7cd:'
                 b' 200 OK Output: OK","ServiceID":"svc-a31a1c88-0633-4e1b-ab74-418e7b39c7cd","ServiceName":"activator-default",'
                 b'"ServiceTags":["noc","svc-a31a1c88-0633-4e1b-ab74-418e7b39c7cd"],"Type":"http","Interval":"10s","Timeout":"1s",'
                 b'"ExposedPort":0,"Definition":{},"CreateIndex":5100630,"ModifyIndex":5100665}]}]\r\n0\r\n\r\n']

# eof_mark = b"</html>\r\n"
# eof_mark = b"\r\n0\r"
eof_mark = b""

def test_parser():
    response_body: List[bytes] = []
    parser = ResponseParser()
    while not parser.is_message_complete():
        response = ls_response_1.pop(0)
        parser.execute(response, eof_mark)
        # print(f'{parser.is_partial_body()=}')
        # print(parser.recv_body())
        # print(f"{parser.is_headers_complete()=}")
        rec = parser.recv_body()
        if len(rec) > 0:
            response_body += [rec]

    # print(parser.get_status_code())
    # print(parser.get_headers())
    # print(f'{parser.is_message_complete()=}')
    # print(b"".join(response_body))

    code = parser.get_status_code()
    headers = parser.get_headers()
    body = b"".join(response_body)
    return code, headers, body


class CB(object):
    @classmethod
    def _status(klass, response, allow_404=True):
        # status checking
        if 400 <= response.code < 500:
            if response.code == 400:
                raise Exception('%d %s' % (response.code, response.body))
            elif response.code == 401:
                raise Exception(response.body)
            elif response.code == 403:
                raise Exception(response.body)
            elif response.code == 404:
                if not allow_404:
                    raise Exception(response.body)
            else:
                raise Exception("%d %s" % (response.code, response.body))
        elif 500 <= response.code < 600:
            raise Exception("%d %s" % (response.code, response.body))

    @classmethod
    def bool(klass):
        # returns True on successful response
        def cb(response):
            CB._status(response)
            return response.code == 200
        return cb

    @classmethod
    def json(
            klass,
            map=None,
            allow_404=True,
            one=False,
            decode=False,
            is_id=False,
            index=False):
        """
        *map* это функция, применяемая к конечному результату.

        *allow_404* если установлено, None будет возвращено в 404 вместо повышения
        NotFound.

        *index* если установлено, будет возвращен кортеж индекса и данных.

        *one* возвращает только первый элемент списка элементов. пустые списки принудительно
         None.

        *decode* если указано, этот ключ будет декодирован в формате Base64.

        *is_id* будет возвращено только поле «ID» объекта json.
        """
        def cb(response):
            CB._status(response, allow_404=allow_404)
            if response.code == 404:
                # return response.headers['X-Consul-Index'], None
                return response.headers['X-Consul-Index'], None

            data = json.loads(response.body)

            if decode:
                for item in data:
                    if item.get(decode) is not None:
                        item[decode] = base64.b64decode(item[decode])
            if is_id:
                data = data['ID']
            if one:
                if data == []:
                    data = None
                if data is not None:
                    data = data[0]
            if map:
                data = map(data)
            if index:
                return response.headers['x-consul-index'], data
            return data
        return cb

def str_title(st:str):
    """ x-consul-index -> X-Consul-Index
    """
    res = '-'.join([s.title() for s in st.split('-')])
    return res


if __name__ == '__main__':
    code, headers, body = test_parser()
    print(f"{code=}, {type(code)=}")
    print(headers)
    print(body)
    # Response = collections.namedtuple('Response', ['code', 'headers', 'body'])
    # response = Response(code=code, headers=headers, body=body)
    # # print(response)
    # f = CB.json(index=True)
    # # f = CB.json()
    # print(f(response))

    # str_title('x-consul-index')


