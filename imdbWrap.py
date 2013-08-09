# This file contains the IMDb wrapper and associated classes used by the
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

import urllib
import urllib2
import HTMLParser

import utils

# TODO: Make the imdb_scrape*() functions return ValueErrors when data cannot
# be scraped
# TODO: Clean up some string code

# Note: the following HTML parsers are very hacky, as they should be. Scraping
# HTML is never a good way of consistently getting data, and while some effort
# has been made to make sure we're looking for the right things during the
# scraping, it is important to realize that not too much effort must be put
# into this task as it can be rendered futile with one small change of HTML
# output on IMDb's part.
#
# Thus, treat the search parser classes as black boxes; generally, they take
# HTML, look for some basic heuristics telling that we're in the right place
# (e.g. we found a "table" tag with the attribute "class='cast'", followed by a
# "td" tag with the attribute "class='name'"), and scrape away.

# This is an HTML parser that takes a string of HTML and returns a search
# results dict mimicking the dict returned by parsing the JSON data from TMDb.
class SearchParser(HTMLParser.HTMLParser):
    def __init__(self):
        self.data = { 'total_results':0, 'results': [] }
        self._result = False
        self._table = False
        self._left = False
        self._leftright = False
        HTMLParser.HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        if self._result == True and tag == 'a':
            self._split1 = attrs[0][1].split('/title/')
            self._split2 = self._split1[1].split('/')
            self.data['results'].append({'id': self._split2[0] })
            self._result = False
        if self._table == True and tag == 'td' and \
          attrs == [('class', 'title')]:
            self._result = True
        if tag == 'table' and attrs == [('class', 'results')]:
            self._table = True

        if self._leftright == True and tag == 'div' and \
          attrs == [('id', 'left')]:
            self._left = True
        if tag == 'div' and attrs == [('class', 'leftright')]:
            self._leftright = True

    def handle_endtag(self, tag):
        if self._left == True and tag == 'div':
            self._left = False

    def handle_data(self, data):
        if self._left == True:
            self._split1 = data.split(' of ')
            self._split2 = self._split1[-1].split('titles')
            self._total_results = \
              int(self._split2[0].replace('\n', '').replace(',', ''))
            self.data.update({'total_results': self._total_results })


# This is an HTML parser that takes a string of HTML and returns a movie info
# dict mimicking the dict returned by parsing the JSON data from TMDb.
class MovieParser(HTMLParser.HTMLParser):
    def __init__(self):
        self.data = { 'title':'', 'release_date':'' }
        self._name = False
        self._name1 = True
        self._meta = True
        HTMLParser.HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        if tag == 'span' and \
          attrs == [('class', 'itemprop'), ('itemprop', 'name')]:
            self._name = True

        if self._meta == True and tag == 'meta' and \
          attrs[0] == ('itemprop', 'datePublished'):
            self._meta = False
            self.data.update({'release_date': attrs[1][1]})

    def handle_data(self, data):
        if self._name == True and self._name1 == True:
            self._name1 = False
            self.data.update({'title': data})


# This is an HTML parser that takes a string of HTML and returns a cast info
# dict mimicking the dict returned by parsing the JSON data from TMDb.
class CastParser(HTMLParser.HTMLParser):
    def __init__(self):
        self.data = { 'cast': [] }
        self._table = False
        self._name = False
        HTMLParser.HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        if self._name == True and tag == 'a':
            self._name = False
            self._split1 = attrs[0][1].split('name/')
            self._split2 = self._split1[1].split('/')
            self.data['cast'].append({'id': self._split2[0]})

        if self._table == True and tag == 'td' and \
          attrs == [('class', 'nm')]:
            self._name = True
        
        if tag == 'table' and attrs == [('class', 'cast')]:
            self._table = True

    def handle_endtag(self, tag):
        if self._table == True and tag == 'table':
            self._table == False


# This is an HTML parser that takes a string of HTML and returns a person info
# dict mimicking the dict returned by parsing the JSON data from TMDb.
class PersonParser(HTMLParser.HTMLParser):
    def __init__(self):
        self.data = { 'name': '', 'birthday': '' }
        self._name = False
        HTMLParser.HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        if tag == 'h1' and \
          attrs == [('class', 'header'), ('itemprop', 'name')]:
            self._name = True

        if tag == 'time' and \
          ('itemprop', 'birthDate') in attrs:
            self.data.update({'birthday': attrs[1][1]})

    def handle_data(self, data):
        if self._name == True:
            self._name = False
            self.data.update({'name': data.replace('\n','')})

# We bother defining the imdb_scrape* functions because in the future, we plan
# on having them raise ValueErrors if the HTML data doesn't appear to be
# correct.
def imdb_scrape_search(page):
    parser = SearchParser()
    parser.feed(page)
    return parser.data


def imdb_scrape_movie(page):
    parser = MovieParser()
    parser.feed(page)
    return parser.data


def imdb_scrape_cast(page):
    parser = CastParser()
    parser.feed(page)
    return parser.data


def imdb_scrape_person(page):
    parser = PersonParser()
    parser.feed(page)
    return parser.data

# This class retrieves data from IMDb given the type of data to retrieve: we
# are currently distinguishing among 'search', 'cast', 'movie', and 'person'.
# The data is stored in self.data. This class is made to mimic the tmdbData
# class as closely as possible (perhaps in the future everything in the world
# will be one giant class, a caste-less system, if you will)
class imdbData:
    # The only thing common to all IMDb queries
    base_url = 'http://www.imdb.com/'

    def __init__(self, id, mode, **kargs):
        # In each data-getting mode, we set up the URL, fetch the page, and
        # feed it to the right scraper. Maybe in the future, we can do this
        # song and dance in one parser class or scraper function or something.
        if mode == 'search':
            self._args = { 'title': id,
                          'title_type': 'feature,tv_movie,short',
                          'view': 'simple',
                          'count': 20 }
            if 'start' in kargs:
                self._args.update(kargs)
            self._url = '%ssearch/title?%s' % (self.base_url,
                                               urllib.urlencode(self._args))
            self._req = urllib2.Request(self._url)
            try:
                self._sock = urllib2.urlopen(self._req)
                self._html = self._sock.read()
                self._sock.close()
            except urllib2.HTTPError as e:
                raise ImdbError(2)
            except urllib2.URLError as e:
                if e.__class__.__name__ != 'HTTPError':
                    raise ImdbError(1)
            else:
                try:
                    self._data = imdb_scrape_search(self._html)
                except ValueError:
                    self.data = None
                    raise ImdbError(3)
                self.data = self._data
        elif mode == 'movie':
            self._url = '%stitle/%s' % (self.base_url, id)
            self._req = urllib2.Request(self._url)
            try:
                self._sock = urllib2.urlopen(self._req)
                self._html = self._sock.read()
                self._sock.close()
            except urllib2.HTTPError as e:
                raise ImdbError(2)
            except urllib2.URLError as e:
                if e.__class__.__name__ != 'HTTPError':
                    raise ImdbError(1)
            else:
                try:
                    self._data = imdb_scrape_movie(self._html)
                except ValueError:
                    self.data = None
                    raise ImdbError(3)
                self.data = self._data
        elif mode == 'cast':
            self._url = '%stitle/%s/fullcredits' % (self.base_url, id)
            self._req = urllib2.Request(self._url)
            try:
                self._sock = urllib2.urlopen(self._req)
                self._html = self._sock.read()
                self._sock.close()
            except urllib2.HTTPError as e:
                raise ImdbError(2)
            except urllib2.URLError as e:
                if e.__class__.__name__ != 'HTTPError':
                    raise ImdbError(1)
            else:
                try:
                    self._data = imdb_scrape_cast(self._html)
                except ValueError:
                    self.data = None
                    raise ImdbError(3)
                self.data = self._data
        elif mode == 'person':
            self._url = '%sname/%s' % (self.base_url, id)
            self._req = urllib2.Request(self._url)
            try:
                self._sock = urllib2.urlopen(self._req)
                self._html = self._sock.read()
                self._sock.close()
            except urllib2.HTTPError as e:
                raise ImdbError(2)
            except urllib2.URLError as e:
                if e.__class__.__name__ != 'HTTPError':
                    raise ImdbError(1)
            else:
                try:
                    self._data = imdb_scrape_person(self._html)
                except ValueError:
                    self.data = None
                    raise ImdbError(3)
                self.data = self._data

# Like the tmdbWrap class in tmdbWrap.py, this class serves as a general
# wrapper for interacting with IMDb: it takes a search argument, conducts a
# search for movies using the imdbData class, retrieves the first page of
# results (if any) as a list of Movie class objects, and handles any errors
# using our custom exceptions. Movie results are asked for at 20 per page, in
# order to make this class as much like tmdbWrap as possible (also, asking for
# more results is asking for trouble, as it would take forever to then load
# the individual movie HTML pages containing the data we like to have upon each
# search). To get the next page of results, there is a defined load_next_page
# method.
class imdbWrap:
    def __init__(self, query):
        self.query = query
        self.movielist = []
        self.totalresults = 0

        try:
            self._returned = imdbData(query, 'search')
        except ImdbError:
            raise
        else:
            for item in self._returned.data['results']:
                try:
                    self.movielist.append(utils.Movie(item['id'], 'imdb'))
                except ImdbError:
                    raise
            self.totalresults = self._returned.data['total_results']

    def load_next_page(self):
        try:
            self._returned = imdbData(self.query, 'search',
                start=len(self.movielist)+1)
        except ImdbError:
            raise
        else:
            for item in self._returned.data['results']:
                try:
                    self.movielist.append(utils.Movie(item['id'], 'imdb'))
                except ImdbError:
                    raise


# This is our custom exception class; error 1 corresponds to a URLError from
# urllib.Request, which typically happens when we can't resolve the DNS name.
# Error 2 corresponds to an HTTPError with code '404', and error 3 corresponds
# to a ValueError raised by the imdb_scrape* functions.
class ImdbError(Exception):
    errors = { 1: 'Cannot get data from IMDb: no internet connection.',
               2: 'Cannot get data from IMDb: bad URL specified.',
               3: 'Cannot get data from IMDb: bad data returned.' }

    def __init__(self, error):
        self.error = error

    def __str__(self):
        return self.errors[self.error]
