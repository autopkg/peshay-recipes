#!/usr/bin/python
#
# Copyright 2016 Andreas Hubert
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""See docstring for OxygenURLProvider class"""
# suppress 'missing class member env'
# pylint: disable=e1101

from __future__ import absolute_import
import re

from autopkglib import Processor, ProcessorError

try:
    from urllib.parse import urlopen  # For Python 3
except ImportError:
    from urllib2 import urlopen  # For Python 2

__all__ = ["OxygenURLProvider"]

URLS = {"Editor": "https://www.oxygenxml.com/xml_editor/download_oxygenxml_editor.html",
        "Author": "https://www.oxygenxml.com/xml_author/download_oxygenxml_author.html",
        "web-author": "https://www.oxygenxml.com/xml_web_author/download_oxygenxml_web_author.html",
        "Developer": "https://www.oxygenxml.com/xml_developer/download_oxygenxml_developer.html",
        "WebHelp": "https://www.oxygenxml.com/xml_webhelp/download_oxygenxml_webhelp.html"}

PLATS = ['Windows64', 'MacOSX', 'Linux64', 'All', 'Eclipse']

import ssl
from functools import wraps


def sslwrap(func):
    """http://stackoverflow.com/a/24175862"""
    @wraps(func)
    def wraps_sslwrap(*args, **kw):
        """Monkey-patch for sslwrap to force TLSv1"""
        kw['ssl_version'] = ssl.PROTOCOL_TLSv1
        return func(*args, **kw)
    return wraps_sslwrap

ssl.wrap_socket = sslwrap(ssl.wrap_socket)


class OxygenURLProvider(Processor):
    """Provides a version and dmg download for the Oxygen product given."""
    description = __doc__
    input_variables = {
        "product_name": {
            "required": True,
            "description":
                "Product to fetch URL for. One of 'Editor', 'Author', 'WebAuthor', 'Developer', 'WebHelp'.",
        },
        "platform_name": {
            "required": True,
            "description":
                "Platform to fetch URL for. One of 'Windows64', 'MacOSX', 'Linux64', 'All', 'Eclipse'.",
        }
    }
    output_variables = {
        "version": {
            "description": "Version of the product.",
        },
        "buildid": {
            "description": "Build id of the product.",
        },
        "url": {
            "description": "Download URL.",
        },
        "filename": {
            "description": "filename of the latest Oxygen product.",
        }
    }

    def main(self):
        prod = self.env.get("product_name")
        if prod not in URLS:
            raise ProcessorError(
                "product_name %s is invalid; it must be one of: %s"
                % (prod, ', '.join(URLS)))
        url = URLS[prod]
        valid_plats = PLATS
        plat = self.env.get("platform_name")
        if plat not in valid_plats:
            raise ProcessorError(
                "platform_name %s is invalid; it must be one of: %s"
                % (plat, valid_plats))
        try:
            self.env["object"] = urlopen(url).read()
        except BaseException as err:
            raise ProcessorError(
                "Unexpected error retrieving product manifest: '%s'" % err)

        substring_version = '<li>Version: ([0-9]+[.]?[0-9]*)'
        substring_buildid = 'Build id: <a href="/build_history.html#[0-9]{10}">([0-9]{10})</a>'
        version = re.search(substring_version, self.env["object"])
        buildid = re.search(substring_buildid, self.env["object"])

        self.env["version"] = version.group(1)
        self.env["buildid"] = buildid.group(1)
        if plat == 'Eclipse':
            download_url = ("https://www.oxygenxml.com/InstData/%s/%s/com.oxygenxml.%s_%s.0.v%s.zip" % (prod, plat, prod.lower(), self.env["version"], self.env["buildid"]))
        elif prod == 'web-author':
            download_url = "http://mirror.oxygenxml.com/InstData/WebAuthor/All/oxygenxml-web-author-all-platforms.zip"
        elif prod == 'WebHelp':
            download_url = "https://www.oxygenxml.com/InstData/Editor/Webhelp/oxygen-webhelp.zip"
        elif prod == 'Editor':
            if plat == 'Windows64':
                download_url = ("http://mirror.oxygenxml.com/InstData/%s/%s/VM/oxygen-64bit.exe" % (prod, plat))
            elif plat == 'Linux64':
                download_url = ("https://www.oxygenxml.com/InstData/%s/%s/VM/oxygen-64bit.sh" % (prod, plat))
            elif plat == 'MacOSX':
                download_url = ("https://www.oxygenxml.com/InstData/%s/%s/VM/oxygen.dmg" % (prod, plat))
            else:
                download_url = ("http://mirror.oxygenxml.com/InstData/%s/%s/VM/oxygen.tar.gz" % (prod, plat))
        else:
            if plat == 'Windows64':
                download_url = ("http://mirror.oxygenxml.com/InstData/%s/%s/VM/oxygen%s-64bit.exe" % (prod, plat, prod))
            elif plat == 'Linux64':
                download_url = ("https://www.oxygenxml.com/InstData/%s/%s/VM/oxygen%s-64bit.sh" % (prod, plat, prod))
            elif plat == 'MacOSX':
                download_url = ("https://www.oxygenxml.com/InstData/%s/%s/VM/oxygen%s.dmg" % (prod, plat, prod))
            else:
                download_url = ("http://mirror.oxygenxml.com/InstData/%s/%s/VM/oxygen%s.tar.gz" % (prod, plat, prod))

        self.env["url"] = download_url
        self.env["filename"] = re.search('/([0-9a-zA-Z-_.]*$)', download_url).group(1)
        self.output("Found Version %s" % self.env["version"])
        self.output("Found Build id %s" % self.env["buildid"])
        self.output("Use URL %s" % self.env["url"])
        self.output("Use filename %s" % self.env["filename"])

if __name__ == "__main__":
    PROCESSOR = OxygenURLProvider()
    PROCESSOR.execute_shell()
