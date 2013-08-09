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
import sys
import getopt

import utils
import tmdbWrap
import imdbWrap


# The following is a function that calculates the age of a person, taking as
# input two datetime arguments (date the actor was born and date the movie
# was shot), and giving as output the age as an integer. All the fuss is due to
# the issue of handling leap years.
def calculate_age(born, event):
    if born is not None and event is not None:
        if (event - born) > datetime.timedelta(days = 0):
            try:
                birthday = born.replace(year=event.year)
            except ValueError:
                birthday = born.replace(year=event.year, day=born.day-1)
            if birthday > event:
                return event.year - born.year - 1
            else:
                return event.year - born.year
        else:
            raise ValueError()
    else:
        raise ValueError()


# This is a function printing information about how to run the program.
def print_usage():
    print('Usage:\nTo automatically fetch the first result, type:\n' \
          'python movie-explorer.py -s \'keyword\' -a\n\n' \
          'To run in interactive mode, type:\n' \
          'python movie-explorer.py -a\n\n' \
          'To display this message, type:\n' \
          'python movie-explorer.py -h')


# This function is only used when not in quiet mode. It presents all of the
# matches to the user's query and asks the user to pick one of the results. It
# returns the ordinal of the movie chosen. It's a little complicated because we
# do not fetch all of the results at once, but rather go page by page (where a
# page is every twenty results), and ask the wrapper to give us the next 20.
def pick_result(query, results):
    print('There is a total of %s result%s matching "%s". ' %
          (results.totalresults, ('s','')[len(results.movielist) is 1],
           query))
    for j in range(0, int(math.floor(results.totalresults / 20))+1):
        print('Displaying results %s-%s.' %
              (20*j+1, min(20*j+20, results.totalresults)))
        for i in range(20*j, min(20*j+20, results.totalresults)):
            if results.movielist[i].releasedate is not None:
                print('[%s] "%s" (%s)' %
                      (i+1, results.movielist[i].title,
                       results.movielist[i].releasedate.year))
            else:
                print('[%s] "%s" (%s)' %
                      (i+1, results.movielist[i].title, 'Unknown'))
        keepgoing = None
        if j != int(math.floor(results.totalresults / 20)):
            while (keepgoing != 'y') and (keepgoing != 'n'):
                keepgoing = raw_input('Display next 20 results y/n?')
            if keepgoing == 'n':
                break
            results.load_next_page()
    currentstr = raw_input('Input the number of the desired film ' \
                           'result: ')
    try:
        current = int(currentstr) - 1
    except ValueError:
        current = -1
    while current not in range(len(results.movielist)):
        currentstr = raw_input('Invalid film result number entered; ' \
                               'try again: ')
        try:
            current = int(currentstr) - 1
        except ValueError:
            current = -1
    if results.movielist[current].releasedate is not None:
        print('You have selected "%s" (%s).' %
              (results.movielist[current].title,
               results.movielist[current].releasedate.year))
    else:
        print('You have selected "%s" (Unknown).' %
              (results.movielist[current].title))
    return current


# This function calculates the cast's average age with all the data we can
# muster; otherwise, we raise our custom MovieError exception
def get_cast_avgage(movie):
    running_age = 0
    unaccounted = 0
    for i in range(len(movie.cast)):
        try:
            age = calculate_age(movie.cast[i].birthday, movie.releasedate)
        except ValueError:
            unaccounted += 1
        else:
            running_age = running_age + age
    if (len(movie.cast)-unaccounted) != 0:
        return round((running_age*1.0)/(len(movie.cast)-unaccounted), 1)
    else:
        raise utils.MovieError(1)


# This function is used only when not in quiet mode
def print_cast_avgage(movie, avgage):
    if len(movie.cast) == 0:
        print('There are no cast data available.')
    else:
        print('The following is a list of the cast members with their ages ' \
              'at the time the film was released:')
        for i in range(len(movie.cast)):
            try:
                age = calculate_age(movie.cast[i].birthday, movie.releasedate)
            except ValueError:
                print('%s - Age Unknown' % movie.cast[i].name)
            else:
                print('%s - Age %s' % (movie.cast[i].name, age))
    if avgage is not None:
        print('The average age of the cast in this film is %s' % avgage)
    else:
        print('There are not enough data to determine the average age of ' \
              'the cast.')


# Note that main() outputs a dict ('toreturn') of things we have calculated. If
# we were given bad flags or if we had a wrapper data error, we return None.
# We also return None if we could not find any matching results. (Perhaps we
# could instead raise a MovieError?)
def main(argv):
    # These store information about the flags provided to the program by the
    # user. By default we run in interactive mode (corresponding to the 'quiet'
    # flag not being set) and do not calculate anything (such as
    # 'cast_avgage'). Quiet mode is entered if the user passes the '-s' flag
    # with some keyword to search for.
    quiet = False
    cast_avgage = False

    # This stores our current movie selection out of a list of Movie classes
    # that we get from our wrapper
    current = 0
    # This is the query to search for in a movie database
    query = ''
    # This is the database wrapper to use when searching for movies; default
    # is tmdb
    database = 'tmdb'
    # This dict stores our calculations to be output
    toreturn = {}

    # Parsing user input
    try:
        opts, args = getopt.getopt(argv[1:], 'has:d:', 
                                   ['help', 'avgage', 'search=', 'database='])
    except getopt.GetoptError:
        print_usage()
        return None
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print_usage()
            return None
        elif opt in ('-s', '--search'):
            quiet = True
            query = arg
        elif opt in ('-d', '--database'):
            database = arg
        elif opt in ('-a', '--avgage'):
            cast_avgage = True

    # Here we test if we are even given anything to do (so far, we have only
    # implemented the cast average age option). If we're given nothing to do,
    # we just give the empty list of our calculations thus far.
    if cast_avgage == False:
        print('No tasks given.')
        print_usage()
        return None

    # Here we test if we are even given a valid database option. This check is
    # also done later, but we should spare the user the question of the film
    # title if they gave us a junk database option in the first place.
    if database != 'imdb' and database != 'tmdb':
        print('Invalid database entered; currently, only \'tmdb\' and ' \
              '\'imdb\' are supported.')
        return None


    # Asking the user for the search keyword if we are in interactive mode
    if quiet == False:
        query = raw_input('Search for the title of a film: ')
    # These next 3 lines are so that we don't have to deal with (non-fatal, of
    # course) errors down the road
    if query == '':
        print('No string given to search for; exiting.')
        return None

    # Here, we query the appropriate database for the search results
    if database == 'tmdb':
        try:
            results = tmdbWrap.tmdbWrap(query)
        except tmdbWrap.TmdbError as e:
            print(e)
            return None
    elif database == 'imdb':
        try:
            results = imdbWrap.imdbWrap(query)
        except imdbWrap.ImdbError as e:
            print(e)
            return None

    # If no results are found, we exit. If results are found, we either pick
    # the first (if in quiet mode), or prompt the user.
    if results.totalresults != 0:
        if quiet == False:
            current = pick_result(query, results)
    else:
        print('No films matching "%s" found; exiting.' % query)
        return None

    # If we cannot populate all the data for our chosen film, we exit
    try:
        results.movielist[current].populate_cast(database)
    except tmdbWrap.TmdbError as e:
        print(e)
        return None

    # Here we calculate any info we might have been asked by the user, and then
    # we return any data we calculate (stored in the 'toreturn' dict)
    if cast_avgage == True:
        try:
            _cast_avgage = get_cast_avgage(results.movielist[current])
        except utils.MovieError:
            _cast_avgage = None
        if quiet == False:
            print_cast_avgage(results.movielist[current], _cast_avgage)
        else:
            print('Average age of the actors in "%s" (%s): %s' %
                  (results.movielist[current].title,
                   results.movielist[current].releasedate.year, _cast_avgage))
        toreturn.update( {'cast_avgage': _cast_avgage} )
    return toreturn


# The usual sentinel
if __name__ == '__main__':
    main(sys.argv)
