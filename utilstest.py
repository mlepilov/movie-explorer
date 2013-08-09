# This file contains unit tests for the utils module, a part of movie-explorer.
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
import imdbWrap
import utils

# TODO: write imovieids and iactorids

# tmovieids is a list of tuples of TMDb ids and expected results; imovieids is
# a list of tubles of IMDb ids and expected results
class Movietest(unittest.TestCase):
    # This is a list of movie IDs, good and bad; testing movie id and the kind
    # of exception that the code raises if the movie ID is bad
    tmovieids = [(-1, None, 3),           # bad: should give good http, no data
                 (123412341234, None, 3), # bad: should give good http, no data
                 (0, None, 3),            # bad: should give good http, no data
                 (2757, 2757, None),      # good
                 ('', None, 3),           # bad: should give bad http
                 ('asdf', None, 3)]       # bad: should give good http, no data

    def testinittmdb(self):
        for movieid, expected, exception in self.tmovieids:
            try:
                test = utils.Movie(movieid, 'tmdb')
            except tmdbWrap.TmdbError as e:
                self.assertEqual(e.error, exception)
            else:
                self.assertEqual(test.tmdbid, expected)

#    def testinitimdb(self):
#        for movieid, expected, exception in self.imovieids:
#            try:
#                test = utils.Movie(movieid, 'imdb')
#            except imdbWrap.ImdbError as e:
#                self.assertEqual(e.error, exception)
#            else:
#                self.assertEqual(test.imdbid, expected)


# tactorids is a list of tuples of TMDb ids and expected results; iactorids is
# a list of tubles of IMDb ids and expected results
class Persontest(unittest.TestCase):
    # This is a list of actor IDs, good and bad; testing actor id
    # Note: this test is identical to the one for the Movie class
    tactorids = [(-1, None, 3),
                (123412341234, None, 3),
                (0, None, 3),
                (2963, 2963, None),
                ('', None, 3),
                ('asdf', None, 3)]

    def testinittmdb(self):
        for actorid, expected, exception in self.tactorids:
            try:
                test = utils.Person(actorid, 'tmdb')
            except tmdbWrap.TmdbError as e:
                self.assertEqual(e.error, exception)
            else:
                self.assertEqual(test.tmdbid, expected)

#    def testinitimdb(self):
#        for actorid, expected, exception in self.iactorids:
#            try:
#                test = utils.Person(actorid, 'imdb')
#            except imdbWrap.ImdbError as e:
#                self.assertEqual(e.error, exception)
#            else:
#                self.assertEqual(test.imdbid, expected)


if __name__ == '__main__':
    unittest.main()
