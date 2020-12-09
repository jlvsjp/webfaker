
# -*- coding: utf-8 -*-

import os
import logging
import threading
from flask import Flask

import IPython


class FakeWeb(object):
    workdir = "."
    app = Flask("Fake Web")
    index = "index.html"
    port = 8088

    @classmethod
    def run(cls, debug=False):
        # cls.app.logger.setLevel(logging.WARN)
        if not debug:
            cls.app.logger.disabled = True
            log = logging.getLogger('werkzeug')
            log.disabled = True

        t = threading.Thread(target=cls._run)
        t.setDaemon(True)
        t.start()
        return "http://127.0.0.1:%s" % cls.port

    @classmethod
    def _run(cls):
        # os.chdir(cls.workdir)
        FakeWeb.app.static_folder = os.path.join(cls.workdir, "static")
        cls.app.run(host="127.0.0.1", port=cls.port)


@FakeWeb.app.route('/login', methods=["POST"])
def login():
    data = '''<script>alert("登录失败！您的浏览器不支持该系统，请下载浏览器插件！");window.location.href=document.referrer;</script>'''
    return data


@FakeWeb.app.route('/Script/BindRegCode', methods=["POST"])
def bind_reg_code():
    print("Script/BindRegCode!!!")
    return ""


@FakeWeb.app.route('/')
def index():
    data = ""
    with open(os.path.join(FakeWeb.workdir, FakeWeb.index), "rb") as rf:
        data = rf.read()

    # logging.warn("index -> %s" % FakeWeb.index)
    # logging.warn("data -> %s" % data)
    return data


if __name__ == "__main__":
    FakeWeb.index = "index.html"
    FakeWeb.run()
    IPython.embed()
