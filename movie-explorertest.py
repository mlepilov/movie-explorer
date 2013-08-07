# This file contains unit tests for the movie-explorer module, a part of
# movie-explorer.
#
# movie-explorer - Search for and display movie information
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
movieexplorer = __import__('movie-explorer')


class maintest(unittest.TestCase):
    # This is a list of queries, good and bad
    commands = [ # good command
                 (['movie-explorer.py', '-a', '-s', 'adaptation'],
                  {'cast_avgage': 43.3}),
                 # good command, no results
                 (['movie-explorer.py', '-a', '-s', ''],
                  None),
                 # good command, returns empty dict by design
                 (['movie-explorer.py', '-h'],
                  None),
                 # good command, returns empty dict by design
                 (['movie-explorer.py', '-s', 'adaptation'],
                  None),
                 # bad command
                 (['movie-explorer.py', '-gF#S', 'asdf'],
                  None)]

    def test(self):
        for command, results in self.commands:
            self.assertEqual(movieexplorer.main(command), results)


class get_cast_avgagetest(unittest.TestCase):
    # This is a list of ids with their average ages
    movieids = [ # year, no birthday info on all of cast ("Adaptation")
                 (2757, 43.3, None),
                 # year, no cast birthdays ("Raiders of the Lost Ark - The
                 # Adaptation")
                 (62128, None, 1),
                 # no year, no cast data (second Cyrillic "Shurik" result)
                 (209040, None, 1),
                 # year, no cast data ("Auto B Good - Hitting the Road")
                 (54334, None, 1) ]

    # Note that we are not handling any assertion errors in the tmdbWrap
    # 'Movie' class; for tests against that class, see tmdbWraptest.py
    def test(self):
        for movieid, expected, exception in self.movieids:
            movie = tmdbWrap.Movie(movieid)
            movie.populate_cast()
            try:
                avgage = movieexplorer.get_cast_avgage(movie)
            except movieexplorer.MovieError as e:
                self.assertEqual(e.error, exception)
            else:
                self.assertEqual(avgage, expected)


if __name__ == '__main__':
    unittest.main()
