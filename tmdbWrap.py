# This file contains the TMDb wrapper and associated classes used by the
# movie-explorer module, a part of movie-explorer.
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

import math
import datetime
import urllib
import urllib2
import json

import utils


# This class retrieves data from TMDb given a location/arguments to the API as
# a dict. The data is stored in self.data.
class tmdbData:
    # These are static class vars that every query to TMDb will have.
    # This is the unique API key for TMDb given to each developer; this
    # particular one belongs to Mikhail Lepilov.
    api_key = 'a1c96b8cef6c9961330b81bd8a508376'
    base_url = 'http://api.themoviedb.org/3/'
    base_args = {'api_key': api_key}

    def __init__(self, url, **kargs):
        # Here we set up the URL, fetch the page, parse the JSON, and store the
        # data as a dict in self.data. We also handle any errors using our
        # custom exceptions.
        self._args = dict(self.base_args, **kargs)
        self._url = '%s%s%s' % \
                     (self.base_url, url, urllib.urlencode(self._args))
        self._req = urllib2.Request(self._url)
        self._req.add_header('Accept', 'application/json')
        self._req.lifetime = 3600
        try:
            self._page = urllib2.urlopen(self._req)
        except urllib2.HTTPError as e:
            if e.code == 401:
                raise TmdbError(2) # This error is thrown if the API key is
                                   # invalid
            elif e.code == 404:    # This error is thrown if we get bad data
                raise TmdbError(3) # or specify an incorrect URL/id
        except urllib2.URLError as e:
            if e.__class__.__name__ != 'HTTPError':
                raise TmdbError(1) # This error is thrown if we cannot resolve
                                   # the URL, among other things
        else:
            try:
                self._data = json.load(self._page)
            except ValueError:
                self.data = None
                raise TmdbError(3)
            self.data = self._data


# This class serves as a general wrapper for interacting with the TMDb API: it
# takes a search argument, conducts a search for movies using the tmdbData
# class, retrieves the first page of results (if any) as a list of Movie class
# objects, and handles any errors using our custom exceptions. Movie results
# are given at 20 per page by the API and are sorted by relevance. To get the
# next page of results, there is a defined load_next_page method.
class tmdbWrap:
    def __init__(self, query):
        self.query = query
        self.movielist = []
        self.totalresults = 0

        try:
            self._returned = tmdbData('search/movie?',
                                      query=self.query, include_adult=False)
        except TmdbError:
            raise
        else:
            for item in self._returned.data['results']:
                try:
                    self.movielist.append(utils.Movie(item['id'], 'tmdb'))
                except TmdbError:
                    raise
            self.totalresults = self._returned.data['total_results']

    # This is the method that fetches the next page of movie results, if any,
    # and handles any errors using our custom exceptions.
    def load_next_page(self):
        try:
            self._returned = tmdbData('search/movie?', query=self.query,
               include_adult=False,
               page=int(math.ceil(len(self.movielist)/20)+1))
        except TmdbError:
            raise
        else:
            for item in self._returned.data['results']:
                try:
                    self.movielist.append(utils.Movie(item['id'], 'tmdb'))
                except TmdbError:
                    raise


# This is our custom exception class; errors 1 and 2 correspond to an HTTPError
# exception obtained when trying to use urllib.Request. (Specifically, 1
# corresponds to HTTP error '404' and 2 corresponds to HTTP error '401'.) Error
# 3 corresponds to a malformed data given by the server but without an HTTP
# error.
class TmdbError(Exception):
    errors = { 1: 'Cannot get data from TMDb: no internet connection.',
               2: 'Cannot get data from TMDb: invalid API key.',
               3: 'Cannot get data from TMDb: bad URL specified.' }

    def __init__(self, error):
        self.error = error

    def __str__(self):
        return self.errors[self.error]
