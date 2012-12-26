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
import mechanize

from bs4 import BeautifulSoup

class MySecondLifeError(Exception):
    pass


class SigninError(MySecondLifeError):
    pass


class MySecondLife(object):
    """A wrapper around the SecondLife account pages (https://secondlife.com/my/account/)

    Because SecondLife offers no API to a lot of the account-related data, we have
    to make do with ugly html scraping that's bound to break horribly whenever
    Linden Lab changes something.
    """
    username = None
    password = None

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.br = mechanize.Browser()
        self.br.set_handle_robots(False) # Required because SL blocks robots
        self._request_page('http://secondlife.com/my/account/') # Ensure we're logged in

    def _request_page(self, url):
        """Requests an account-protected page

        Will perform a sign in if not yet signed in"""
        br = self.br
        br.open(url)
        if br.title() == "OpenId transaction in progress":
            br.select_form(nr=0)
            br.submit()
        if br.title() == "Second Life: Sign In":
            br.select_form(nr=0)
            br['username'] = self.username
            br['password'] = self.password
            br.submit()
            assert br.title() == "OpenId transaction in progress" or br.title() == "Second Life: Sign In"
            if br.title() == "Second Life: Sign In":
                try:
                    soup = BeautifulSoup(br.response().read())
                    errormsg = [s for s in soup.find_all("div", class_="error")[0].strings]
                    error = " ".join(["Sign in failed with the following error:"] + errormsg)
                except Exception as e:
                    logging.exception(e)
                    error = ("Expected an OpenId transaction, but ended back up at the "
                             "sign in form and couldn't locate an error message")
                raise SigninError(error)
            br.select_form(nr=0)
            br.submit()
        return BeautifulSoup(br.response().read())

    def _extract_friends_from_html_soup(self, soup):
        """Extract online friends from the html of the friends-online page"""
        friends = []
        friendsoup = soup.find_all("div", class_="main-content-body")
        assert len(friendsoup) == 1
        friendsoup = friendsoup[0].find_all("li")
        for spoonful in friendsoup:
            strings = [s for s in spoonful.strings]
            logging.debug("Found friend {}".format(strings))
            friends.append(" ".join(strings))
        return friends

    def friends_online(self):
        """Return a list of online friends"""
        html = self._request_page("https://secondlife.com/my/account/friends.php?")
        assert html.title.string == "Friends Online | Second Life"
        return self._extract_friends_from_html_soup(html)
