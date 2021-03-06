# This file contains unit tests for the tmdbWrap module, a part of
# movie-explorer.
#
# movie-explorer - Search for and display movie information.
# Copyright (C) 2013 Mikhail Lepilov
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTIBILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
#
# For questions or concerns, contact Mikhail Lepilov at mlepilov@gmail.com
#
# This product uses the TMDb API but is not endorsed or certified by TMDb.

import unittest

import tmdbWrap


class tmdbWraptest(unittest.TestCase):
    # This is a list of queries, good and bad; testing # results
    keywords = [ # API handles empty strings by returning 0
                 ('', 0),
                 # improbable query with a lot of results
                 ('a', 10191),
                 # typical query with no results
                 ('asdfasdfjsdfjsakf', 0),
                 # has a special character, no results
                 ('_As\'fr$%@^234', 0),
                 # typical query with a few results
                 ('adaptation', 2),
                 # typical query with a lot of results, again 20 at a time
                 ('good', 361),
                 # has special characters and a few results
                 ('\\u0448\\u0443\\u0440\\u0438\\u043A\\u0430', 3) ]

    def testinit(self):
        for keyword, expected in self.keywords:
            try:
                test = tmdbWrap.tmdbWrap(keyword)
            except tmdbWrap.TmdbError:
                pass
            else:
                self.assertEqual(test.totalresults, expected)


if __name__ == '__main__':
    unittest.main()
