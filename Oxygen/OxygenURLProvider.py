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
#pylint: disable=e1101

import urllib2
import plistlib
from distutils.version import LooseVersion
from operator import itemgetter

from autopkglib import Processor, ProcessorError

__all__ = ["OxygenURLProvider"]

URLS = {"Editor": "https://www.oxygenxml.com/xml_editor/download_oxygenxml_editor.html",
        "Author": "https://www.oxygenxml.com/xml_author/download_oxygenxml_author.html",
        "WebAuthor": "https://www.oxygenxml.com/xml_web_author/download_oxygenxml_web_author.html",
        "Developer": "https://www.oxygenxml.com/xml_developer/download_oxygenxml_developer.html",
        "WebHelp": "https://www.oxygenxml.com/xml_webhelp/download_oxygenxml_webhelp.html"}

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
        '''Find the download URL'''
        def compare_version(this, that):
            '''compare LooseVersions'''
            return cmp(LooseVersion(this), LooseVersion(that))

        valid_prods = URLS.keys()
        prod = self.env.get("product_name")
        if prod not in valid_prods:
            raise ProcessorError(
                "product_name %s is invalid; it must be one of: %s"
                % (prod, valid_prods))
        url = URLS[prod]
        try:
            self.env["object"] = urllib2.urlopen(url).read()
        except BaseException as err:
            raise ProcessorError(
                "Unexpected error retrieving product manifest: '%s'" % err)

        substring_version = 'Version: \([0-9]*\)'
        substring_buildid = 'Build id: <a href="/history.html#\([0-9]{10}\)'
        download_url = ("http://mirror.oxygenxml.com/InstData/Author/MacOSX/VM/oxygen%s.tar.gz" % prod)
        version = re.search(substring_version, self.env["object"])
        buildid = re.search(substring_buildid, self.env["object"])
        self.env["url"] = download_url
        self.env["filename"] = ("oxygen%s.tar.gz" % prod)
        self.env["version"] = version.group(1)
        self.env["buildid"] = buildid.group(1)
        self.output("Found Version %s" % self.env["version"])
        self.output("Found Build id %s" % self.env["buildid"])
        self.output("Found URL %s" % self.env["url"])
        self.output("Use filename %s" % self.env["filename"])

if __name__ == "__main__":
    PROCESSOR = OxygenURLProvider()
    PROCESSOR.execute_shell()
