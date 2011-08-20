'''
    letmewatchthis XBMC Addon
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
'''

import re
import string
import sys
from t0mm0.common.addon import Addon
from t0mm0.common.net import Net
import urlresolver

addon = Addon('plugin.video.letmewatchthis', sys.argv)
net = Net()

base_url = 'http://www.letmewatchthis.ch'

mode = addon.queries['mode']
play = addon.queries.get('play', None)

if play:
    try:
        addon.log_debug('fetching %s' % play)
        html = net.http_GET(play).content
    except urllib2.URLError, e:
        html = ''
        addon.log_error('got http error %d fetching %s' %
                        (e.code, web_url))
    
    #find all sources and their info
    sources = {}
    for s in re.finditer('class="movie_version".+?quality_(.+?)>.+?url=(.+?)' + 
                         '&domain=(.+?)&.+?"version_veiws">(.+?)</', 
                         html, re.DOTALL):
        q, url, host, views = s.groups()
        verified = s.group(0).find('star.gif') > -1
        source =  host.decode('base-64')
        if verified:
            source += ' [verified]'
        source += ' (%s)' % views.strip()
        sources[url.decode('base-64')] = source
    
    stream_url = urlresolver.choose_source(sources)    
    addon.resolve_url(stream_url)

elif mode == 'browse':
    browse = addon.queries.get('browse', False)
    letter = addon.queries.get('letter', False)
    section = addon.queries.get('section', '')
    if letter:        
        html = '> >> <'
        page = 0
        while html.find('> >> <') > -1:
            page += 1
            url = '%s/?letter=%s&sort=alphabet&page=%s&%s' % (base_url, letter, 
                                                              page, section)
            try:
                addon.log_debug('fetching %s' % url)
                html = net.http_GET(url).content
            except urllib2.URLError, e:
                html = ''
                addon.log_error('got http error %d fetching %s' %
                                (e.code, web_url))

            r = re.search('number_movies_result">(\d+)', html)
            if r:
                total = int(r.group(1))
            else:
                total = 0
                
            r = 'class="index_item.+?href="(.+?)".+?src="(.+?)".+?' + \
                'alt="Watch (.+?)"'
            regex = re.finditer(r, html, re.DOTALL)
            for s in regex:
                url, thumb, title = s.groups()
                addon.add_directory({'mode': 'series', 
                                     'url': base_url + url}, 
                                     title, 
                                     img=thumb,
                                     total_items=total)
            

    else:
            addon.add_directory({'mode': 'browse', 
                                 'section': section,
                                 'letter': '123'}, '#')
            for l in string.uppercase:
                addon.add_directory({'mode': 'browse', 
                                     'section': section,
                                     'letter': l}, l)
        
elif mode == 'series':
    url = addon.queries['url']
    try:    
        addon.log_debug('fetching %s' % url)
        html = net.http_GET(url).content
    except urllib2.URLError, e:
        html = ''
        addon.log_error('got http error %d fetching %s' %
                        (e.code, web_url))
                        
    regex = re.search('movie_thumb"><img src="(.+?)"', html)
    if regex:
        img = regex.group(1)
    else:
        addon.log_error('couldn\'t find image')
        img = ''
    
    seasons = re.search('tv_container(.+?)<div class="clearer', html, re.DOTALL)    
    if not seasons:
        addon.log_error('couldn\'t find seasons')
    else:
        for season in seasons.group(1).split('<h2>'):
            r = re.search('<a.+?>(.+?)</a>', season)
            if r:
                season_name = r.group(1)
            else:
                season_name = 'Unknown Season'
                addon.log_error('couldn\'t find season title')

            r = '"tv_episode_item".+?href="(.+?)">(.*?)</a>'
            episodes = re.finditer(r, season, re.DOTALL)
            for ep in episodes:
                url, title = ep.groups()
                title = re.sub('<[^<]+?>', '', title.strip())
                title = re.sub('\s\s+' , ' ', title)
                addon.add_video_item(base_url + url, {'title': '%s %s' % 
                                                 (season_name, title)}, img=img)


elif mode == 'main':
    addon.add_directory({'mode': 'browse', 'section': 'tv'}, 'TV')
    addon.add_directory({'mode': 'resolver_settings'}, 'Resolver Settings', 
                        is_folder=False)

elif mode == 'resolver_settings':
    urlresolver.display_settings()


if not play:
    addon.end_of_directory()


