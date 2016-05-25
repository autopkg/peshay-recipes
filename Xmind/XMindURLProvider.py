#!/usr/bin/env python
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

import re
import urllib2, json

from autopkglib import Processor, ProcessorError


__all__ = ["XMindUrlProvider"]


BASE_URL = "http://www.xmind.net/download/mac/"


class XMindURLProvider(Processor):
    """Provides a download URL for the latest Xmind release."""
    input_variables = {
        "base_url": {
            "required": False,
            "description": "Default is %s" % BASE_URL,
        },
    }
    output_variables = {
        "url": {
            "description": "URL to the latest XMind release.",
        },
        "date": {
            "description": "Release date of the latest XMind release.",
        },
        "version": {
            "description": "Version of the latest XMind release.",
        },
    }
    description = __doc__

    def get_xmind_url(self, base_url):
        try:
            url = urllib2.urlopen(base_url).read()
            return url

        except BaseException as err:
            raise Exception("Can't read %s: %s" % (base_url, err))

    def main(self):
        """Find and return a download URL"""
        base_url = self.env.get("base_url", BASE_URL)
        substring_version = 'The latest release is XMind 7 ' +\
                            '\(v([0-9].[0-9].[0-9])\)'
        substring_url = 'href="(http://www.xmind.net/xmind/downloads/.*.dmg)">'
        latest = re.search(substring_version, base_url)
        download = re.search(substring_url, base_url)
        self.env["object"] = self.get_xmind_url(base_url)
        self.env["url"] = download.group(1)
        self.env["version"] = latest.group(1)
        self.output("Found URL %s" % self.env["url"])


if __name__ == "__main__":
	processor = XMindURLProvider()
	processor.execute_shell()
