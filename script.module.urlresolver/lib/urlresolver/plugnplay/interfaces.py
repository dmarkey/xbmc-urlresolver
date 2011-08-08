"""
    urlresolver XBMC Addon
    Copyright (C) 2011 t0mm0

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import urlresolver
from urlresolver import common
from urlresolver.plugnplay import Interface
import sys

def _function_id(obj, nFramesUp):
	""" Create a string naming the function n frames up on the stack. """
	fr = sys._getframe(nFramesUp+1)
	co = fr.f_code
	return "%s.%s" % (obj.__class__, co.co_name)

def not_implemented(obj=None):
	""" Use this instead of 'pass' for the body of abstract methods. """
	raise Exception("Unimplemented abstract method: %s" % _function_id(obj, 1))


class UrlResolver(Interface):
    name = 'override_me'
    priority = 100
    profile_path = common.profile_path
    
    def get_media_url(self, web_url):
        not_implemented(self)
    
    def valid_url(self, web_url):
        not_implemented(self)
    
    def get_media_urls(self, web_urls):
        ret_val = []
        for web_url in web_urls:
            url = self.get_media_url(web_url)
            if url:
                ret_val.append(url)
        return ret_val
    
    def filter_urls(self, web_urls):
        ret_val = []
        for web_url in web_urls:
            valid = self.valid_url()
            if valid:
                ret_val.append(web_url)
        return

class SiteAuth(Interface):
    def login(self, username, password):
        not_implemented(self)

class PluginSettings(Interface):
    def get_settings_xml(self):
        xml = '<category label="%s">\n' % self.name
        xml += '<setting id="%s_priority" ' % self.name
        xml += 'type="number" label="Priority" default="100"/>\n'
        xml += '</category>\n'
        return xml 
        
    def get_setting(self, key):
        value = common.addon.get_setting('%s_%s' % (self.name, key))
        return value
    
