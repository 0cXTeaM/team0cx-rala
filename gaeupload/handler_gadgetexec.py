# handler_gadgetexec.py
#
#

""" jsonbot exec handler.  just return the results in a <div>. """

## gozerlib imports

from gozerlib.utils.generic import fromenc, toenc, getversion
from gozerlib.utils.xmpp import stripped
from gozerlib.plugins import plugs
from gozerlib.persist import Persist
from gozerlib.utils.exception import handle_exception
from gozerlib.boot import boot
from gozerlib.fleet import fleet
from gozerlib.config import cfg as maincfg
from gozerlib.errors import NoSuchCommand

## gaelib imports

from gozerlib.gae.wave.bot import WaveBot
from gozerlib.gae.web.bot import WebBot
from gozerlib.gae.web.event import WebEvent
from gozerlib.gae.utils.web import execbox, commandbox, closer

## google imports

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.api import users as gusers

## simplejson import

from simplejson import loads

## basic imports

import wsgiref.handlers
import sys
import time
import types
import os
import logging

logging.warn(getversion('GADGETEXEC'))

#webbot = WebBot()
wavebot = WaveBot()

class HB_Handler(webapp.RequestHandler):

    """ the bots exec command dispatcher. """

    def get(self):
        commandbox(self.response, "/gadgetexec/")

    def post(self):

        """ this is where the command get disaptched. """

        logging.debug("HBEXEC incoming: %s" % self.request.remote_addr)
        event = WebEvent().parse(self.response, self.request)
        event.bot = wavebot
        event.cbtype = 'HBEXEC'
        event.iswave = True
        event.isgadget = True

        try:
            wavebot.doevent(event)

        except NoSuchCommand:
            event.reply("no %s command found" % event.usercmnd)
        except Exception, ex:
            handle_exception(event)

# the application 

application = webapp.WSGIApplication([('/gadgetexec', HB_Handler),
                                      ('/gadgetexec/', HB_Handler)],
                                      debug=True)

def main():
    global webbot
    global application
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
