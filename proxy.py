
import re
import os
import ssl
import pdb
import json
import socket
import logging
import threading

from urlparse import urlparse
from SocketServer import BaseRequestHandler, TCPServer

import IPython
from http_parser.http import HttpParser


TCPServer.allow_reuse_address = True


class ProxyHandler(object):
    domain = None
    bind = 80
    path = None
    host = ""
    port = 80
    ishttps = False
    record_file = "record.csv"
    ext_file = None

    @classmethod
    def handle(cls, msg):
        parser = HttpParser()
        parser.execute(msg, len(msg))

        url = parser.get_url()
        if cls.path and cls.path in url:
            cls.record(
                "%s://%s%s" % (str("https" if cls.ishttps else "http"),
                               cls.host, url),
                json.dumps(parser.get_headers()),
                parser.recv_body()
            )

        # Support extension
        callback = None
        if cls.ext_file:
            ext = __import__(cls.ext_file[:-3]).EXT
            callback = ext.do(url)

        return cls.send(msg, callback)

    @classmethod
    def send(cls, msg, callback=None):
        _sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if cls.ishttps:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            sock = context.wrap_socket(
                _sock,
                do_handshake_on_connect=True,
                server_hostname=cls.host
            )
        else:
            sock = _sock

        sock.settimeout(3)
        while True:
            try:
                sock.connect((cls.host, cls.port))
                break
            except Exception:
                pass

        host = None
        regx = re.compile(r"\r\n[Hh]ost: (?P<host>.+)\r\n")
        try:
            host = regx.findall(msg)[0]
            old1 = str("\r\nHost: %s\r\n" % host.strip()).encode()
            old2 = str("\r\nhost: %s\r\n" % host.strip()).encode()
            new = str("\r\nHost: %s\r\n" % cls.host).encode()

            if cls.port != 80 and cls.port != 443:
                new += str(":%s" % cls.port).encode()

            msg = msg.replace(old1, new)
            msg = msg.replace(old2, new)

        except Exception:
            logging.error("Replace host error -> %s" % msg)
            return b""

        regx2 = re.compile(r"\r\nAccept-Encoding: (?P<encode>.+)[\r\n]?")
        try:
            encode = regx2.findall(msg)[0]
            old = str("\r\nAccept-Encoding: %s\r\n" % encode.strip()).encode()
            new = b"\r\n"
            msg = msg.replace(old, new)
        except Exception:
            if "Accept-Encoding:" in msg:
                logging.error("Replace encode error -> %s" % msg)

        msg = msg.replace("connection: keep-alive", "Connection: Close")
        msg = msg.replace("Connection: keep-alive", "Connection: Close")
        msg = msg.replace("Connection: Keep-Alive", "Connection: Close")

        logging.debug("-----------\nRequest ->\n%s\n" % msg)
        sock.send(msg)

        ret = b""
        while True:
            try:
                _ret = sock.recv(1024)
            except socket.timeout:
                logging.error("resp socket.timeout")
                break

            if not _ret or len(_ret) == 0:
                break

            ret += _ret

        sock.close()
        if host:
            old = str("http%s://%s" % ("s" if cls.ishttps else "", cls.host)).encode()
            new = str("http://%s" % host)
            if cls.port != 80 and cls.port != 443:
                old += str(":%s" % cls.port).encode()
            ret = ret.replace(old, new)

            old = cls.host
            new = host
            if cls.port != 80 and cls.port != 443:
                old += str(":%s" % cls.port).encode()
            ret = ret.replace(old, new)

        # EXTENSION
        if callback:
            _header, _body = tuple(ret.split("\r\n\r\n"))
            header, body = callback(_header, _body)
            ret = "%s\r\n\r\n%s" % (header, body)

        ret = cls.patch(ret)
        logging.debug("Response ->\n%s\n" % ret[:1024])
        return ret

    @classmethod
    def patch(cls, ret):
        try:
            _ret_spl = ret.split(b"\r\n\r\n")
            header = _ret_spl[0]
            body = b"\r\n\r\n".join(_ret_spl[1:])
            new_content_length = len(body)

            regx = re.compile(r"\r\nContent-Length: (?P<length>\d+)[\r\n]?")
            old_content_length = regx.findall(header)[0]
            old = str("\r\nContent-Length: %s\r\n" % old_content_length.strip()).encode()
            new = str("\r\nContent-Length: %d\r\n" % new_content_length).encode()
            ret = ret.replace(old, new)
        except Exception as e:
            # pdb.set_trace()
            logging.error("patch error! - %s\n%s" % (e, ret[:1024]))

        return ret


    @classmethod
    def record(cls, url, headers, post_body):
        logging.warn("Get post_body -> %s" % post_body)

        if not os.path.exists(cls.record_file):
            with open(cls.record_file, "wb") as wr:
                wr.write("url,headers,post_body\n")

        with open(cls.record_file, "a+") as wr:
            wr.write("%s,%s,%s\n" % (url, headers, post_body))


class ProxyRequestHandler(BaseRequestHandler):
    def handle(self):
        logging.debug('Got connection from [%s:%s]\n' % self.client_address)
        msg = b""
        self.request.settimeout(3)
        while True:
            try:
                _msg = self.request.recv(1024)
            except socket.timeout:
                logging.warn('Timeout - %s:%s\n' % self.client_address)
                break

            if not _msg or len(_msg) == 0:
                break

            msg += _msg
            if len(_msg) < 1024:
                break

        ret = ProxyHandler.handle(msg)
        i = 0
        total = 0
        while True:
            data = ret[i * 1024: i * 1024 + 1024]
            total += self.request.send(data)
            i += 1
            if len(data) < 1024:
                break
        logging.debug("Send response %d" % total)


class ProxyServer(TCPServer):

    def __init__(self, url, path=None, port=8888):
        self.port = port
        ProxyHandler.bind = port

        purl = urlparse(url)
        ProxyHandler.host = purl.hostname
        ProxyHandler.ishttps = True if purl.scheme == "https" else False
        ProxyHandler.port = purl.port if purl.port else 443 if ProxyHandler.ishttps else 80
        ProxyHandler.path = path

        # pdb.set_trace()
        TCPServer.__init__(self, ('0.0.0.0', self.port), ProxyRequestHandler)

    def run(self):
        t = threading.Thread(target=self.serve_forever)
        t.setDaemon(True)
        t.start()
        logging.info("Proxy server bind on port %d" % self.port)


if __name__ == '__main__':
    ps = ProxyServer()
    ps.run()
    IPython.embed()
