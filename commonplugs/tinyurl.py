# commonplugs/tinyurl.py
#
#

""" tinyurl.com feeder """

__author__ = "Wijnand 'tehmaze' Modderman - http://tehmaze.com"
__license__ = 'BSD'

## gozerlib imports

from gozerlib.commands import cmnds
from gozerlib.utils.url import striphtml, useragent
from gozerlib.examples import examples

## google imports

try:
    from google.appengine.api.memcache import get, set
    import google
except ImportError:
    def get(name, *args, **kwargs):
        return ""
    def set(name, value, *args, **kwargs):
        return ""

## simpljejson

from simplejson import dumps, loads

## basic imports

import urllib
import urllib2
import urlparse
import re
import logging

## defines

re_url_match  = re.compile(u'((?:http|https)://\S+)')
urlcache = {}

## functions

def valid_url(url):
    """ check if url is valid """
    if not re_url_match.search(url):
        return False
    parts = urlparse.urlparse(url)
    cleanurl = '%s://%s' % (parts[0], parts[1])
    if parts[2]:
        cleanurl = '%s%s' % (cleanurl, parts[2])
    if parts[3]:
        cleanurl = '%s;%s' % (cleanurl, parts[3])
    if parts[4]:
        cleanurl = '%s?%s' % (cleanurl, parts[4])
    return cleanurl


def precb(bot, ievent):
    test_url = re_url_match.search(ievent.txt)
    if test_url:
        return 1

def privmsgcb(bot, ievent):
    """ callback for urlcaching """
    test_url = re_url_match.search(ievent.txt)
    if test_url:
        url = test_url.group(1)
        if not urlcache.has_key(bot.name):
            urlcache[bot.name] = {}
        urlcache[bot.name][ievent.target] = url

#callbacks.add('PRIVMSG', privmsgcb, precb)

def get_tinyurl(url):
    """ grab a tinyurl. """
    res = get(url, namespace='tinyurl')
    logging.debug('tinyurl - cache - %s' % unicode(res))

    if res and res[0] == '[':
        return loads(res)
    
    postarray = [
        ('submit', 'submit'),
        ('url', url),
        ]
    postdata = urllib.urlencode(postarray)
    req = urllib2.Request(url='http://tinyurl.com/create.php', data=postdata)
    req.add_header('User-agent', useragent())
    try:
        res = urllib2.urlopen(req).readlines()
        #raise Exception("mekker")
    except google.appengine.api.urlfetch_errors.DownloadError, e:
        logging.error('tinyurl - %s - DownError: %s' % (url, str(e)))
        return

    except urllib2.URLError, e:
        logging.error('tinyurl - %s - URLError: %s' % (url, str(e)))
        return
    except urllib2.HTTPError, e:
        logging.error('tinyurl - %s - HTTP error: %s' % (url, str(e)))
        return
    urls = []
    for line in res:
        if line.startswith('<blockquote><b>'):
            urls.append(striphtml(line.strip()).split('[Open')[0])
    if len(urls) == 3:
        urls.pop(0)
    set(url, dumps(urls), namespace='tinyurl')
    return urls

def handle_tinyurl(bot, ievent):
    """ get tinyurl from provided url. """
    if not ievent.rest and (not urlcache.has_key(bot.name) or not \
urlcache[bot.name].has_key(ievent.target)):
        ievent.missing('<url>')
        return
    elif not ievent.rest:
        url = urlcache[bot.name][ievent.target]
    else:
        url = ievent.rest
    url = valid_url(url)
    if not url:
        ievent.reply('invalid or bad URL')
        return
    tinyurl = get_tinyurl(url)
    if tinyurl:
        ievent.reply(' .. '.join(tinyurl))
    else:
        ievent.reply('failed to create tinyurl')

cmnds.add('tinyurl', handle_tinyurl, ['USER', 'GUEST'], threaded=True)
examples.add('tinyurl', 'show a tinyurl', 'tinyurl http://jsonbot.googlecode.com')
