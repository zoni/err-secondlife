#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import logging

from errbot import BotPlugin, botcmd

# Hack to ensure we can import secondlife
from sys import path
from os.path import dirname, realpath
path.append(dirname(realpath(__file__)))

from secondlife import MySecondLife

class SecondLife(BotPlugin):
    """Integrating your Second Life into Err"""
    min_err_version = '1.6.0' # Optional, but recommended
    max_err_version = '1.7.1' # Optional, but recommended

    def activate(self):
        if not self.config or not set(self.config).issuperset(set(("USERNAME", "PASSWORD"))):
            logging.info("SecondLife plugin not configured, aborting activation")
        else:
            self.mysl = MySecondLife(self.config['USERNAME'], self.config['PASSWORD'])
            super(SecondLife, self).activate()

    def get_configuration_template(self):
        return {'USERNAME': "some.resident", 'PASSWORD': "secret"}

    @botcmd(split_args_with=None)
    def secondlife_friends(self, mess, args):
        """Tells you which of your friends are currently online"""
        friends = self.mysl.friends_online()
        return u"You currently have {} friends online:\n{}".format(len(friends), u"\n".join(friends))
