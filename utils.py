# This file contains the Movie and Person classes used by the movie-explorer
# module, a part of movie-explorer.
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

import datetime

import tmdbWrap
import imdbWrap


# This class takes an id and a database that the id belongs to and fetches
# movie information using the appropriate wrapper (in an imdbWrap or tmdbWrap
# class). When done fetching data it populates some class objects, like the
# title of the movie or its release date (or initializes "None", if, for
# example, some field is missing or has strange data). Errors are handled using
# a custom exception class.
#
# After we initialize the class, we store the database used so that we have the
# option of not mixing databases when populating the information about a movie
# (but this can currently be done, so we can get search results using TMDb but
# cast data using IMDb, or vice versa).
class Movie:
    def __init__(self, id, database):
        if database == 'tmdb':
            try:
                self._returned = tmdbWrap.tmdbData('movie/%s?' % id)
            except tmdbWrap.TmdbError:
                raise
            else:
                self.tmdbid = self._returned.data['id']
                self.title = self._returned.data['title']
                self.originaltitle = self._returned.data['original_title']
                self.cast = []
                try:
                    self.releasedate = datetime.datetime.strptime( \
                        self._returned.data['release_date'], '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    self.releasedate = None
        elif database == 'imdb':
            try:
                self._returned = imdbWrap.imdbData(id, 'movie')
            except imdbWrap.ImdbError:
                raise
            else:
                self.imdbid = id
                self.title = self._returned.data['title']
                self.cast = []
                try:
                    self.releasedate = datetime.datetime.strptime( \
                        self._returned.data['release_date'], '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    self.releasedate = None
        else:
            raise MovieError(2)


    def populate_cast(self, database):
        self._cast = []
        if database == 'tmdb':
            try:
                self._returned = tmdbWrap.tmdbData('movie/%s/casts?' %
                                                   self.tmdbid)
            except tmdbWrap.TmdbError:
                raise
            else:
                for item in self._returned.data['cast']:
                    try:
                        self._cast.append(Person(item['id'], database))
                    except tmdbWrap.TmdbError:
                        raise
        elif database == 'imdb':
            try:
                self._returned = imdbWrap.imdbData(self.imdbid, 'cast')
            except imdbWrap.ImdbError:
                raise
            else:
                for item in self._returned.data['cast']:
                    try:
                        self._cast.append(Person(item['id'], database))
                    except imdbWrap.ImdbError:
                        raise
        else:
            raise MovieError(2)
        self.cast = self._cast


# Same deal as the Movie class above.
class Person:
    def __init__(self, id, database):
        if database == 'tmdb':
            try:
                self._returned = tmdbWrap.tmdbData('person/%s?' % id)
            except tmdbWrap.TmdbError:
                raise
            else:
                self.tmdbid = self._returned.data['id']
                self.name = self._returned.data['name']
                try:
                    self.birthday = datetime.datetime.strptime( \
                        self._returned.data['birthday'], '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    self.birthday = None
        elif database == 'imdb':
            try:
                self._returned = imdbWrap.imdbData(id, 'person')
            except imdbWrap.ImdbError:
                raise
            else:
                self.imdbid = id
                self.name = self._returned.data['name']
                try:
                    self.birthday = datetime.datetime.strptime( \
                        self._returned.data['birthday'], '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    self.birthday = None
        else:
            raise MovieError(2)


# This is our custom exception class that contains all the errors that may
# arise when being returned incomplete data or when asking to use some
# unrecognized database.
class MovieError(Exception):
    errors = { 1: 'Cannot determine the cast average age.',
               2: 'Invalid movie database specified.' }

    def __init__(self, error):
        self.error = error

    def __str__(self):
        return self.errors[self.error]
