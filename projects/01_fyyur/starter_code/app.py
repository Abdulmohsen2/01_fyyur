#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy.orm import query
from forms import *
from flask_migrate import Migrate
from datetime import datetime
from models import db, Venue, Artist, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    data = []
    Now = datetime.now()
    CityAndState = ''

    venues = Venue.query.group_by(Venue.id, Venue.state, Venue.city).all()

    for venue in venues:
        NextShow = venue.shows

        NextShowsFilter = [
            time for time in NextShow if time.start_time > Now]

        if CityAndState == venue.city + venue.state:
            data[len(data) - 1]["venues"].append({
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(NextShowsFilter)
            })
        else:
            CityAndState == venue.city + venue.state
            data.append({
                "city": venue.city,
                "state": venue.state,
                "venues": [{
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": len(NextShowsFilter)
                }]
            })

    return render_template('pages/venues.html', areas=data)
    # TODO: replace with real venues data.


@app.route('/venues/search', methods=['POST'])
def search_venues():

    search_term = request.form.get('search_term', '')
    results = Venue.query.filter(Venue.name.ilike(f'%{search_term}%'))
    resultsCounts = results.count()
    response = {
        "count": resultsCounts,
        "data": results
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

    venue = Venue.query.get(venue_id)
    shows = Show.query.filter_by(venue_id=venue_id).all()
    Finished_shows = []
    Finished_shows_count = 0
    Next_shows = []
    Next_shows_count = 0
    TimeNow = datetime.now()

    for shows in shows:
        artist = Artist.query.get(shows.artist_id)
        data = {
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": format_datetime(str(shows.start_time))
        }
        if shows.start_time < TimeNow:
            Finished_shows.append(data)
        else:
            Next_shows.append(data)

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": Finished_shows,
        "upcoming_shows": Next_shows,
        "past_shows_count": len(Finished_shows),
        "upcoming_shows_count": len(Next_shows)
    }

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@ app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@ app.route('/venues/create', methods=['POST'])
def create_venue_submission():

    form = VenueForm(request.form)
    try:

        db.session.add(Venue(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            address=form.address.data,
            phone=form.phone.data,
            image_link=form.image_link.data,
            genres=form.genres.data,
            website_link=form.website_link.data,
            facebook_link=form.facebook_link.data,
            seeking_talent=form.seeking_talent.data,
            seeking_description=form.seeking_description.data,
        ))
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:

        db.session.rollback()
        flash('An error occurred. Venue' +
              request.form['name'] + ' could not be listed')
    finally:
        db.session.close()

    return render_template('pages/home.html')


@ app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

    try:
        Deletveenue = Venue.query.get(venue_id)
        db.session.delete(Deletveenue)
        db.session.commit()
        flash('venue has been deleted')

    except:
        db.session.rollback()
        flash('An error occur, and venue has been not deleted')

    finally:
        db.session.close()

        return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------


@ app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = []
    for artist in Artist.query.all():
        data.append({
            "id": artist.id,
            "name": artist.name
        })
    return render_template('pages/artists.html', artists=data)


@ app.route('/artists/search', methods=['POST'])
def search_artists():

    search_term = request.form.get('search_term', '')
    results = Artist.query.filter(Artist.name.ilike(f'%{search_term}%'))
    resultsCounts = results.count()
    response = {
        "count": resultsCounts,
        "data": results
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@ app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

    # 1- Created,2- Tested, (Done with some Notes)

    artist = Artist.query.get(artist_id)
    shows = Show.query.filter_by(artist_id=artist_id)
    Now = datetime.now()
    Previus_shows_list = []
    Future_Show_list = []

    for shows in shows:
        venue = Venue.query.get(shows.venue_id)
        data = {
            "venue_id": venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": str(shows.start_time),
        }
        if shows.start_time < Now:
            Previus_shows_list.append(data)
        else:
            Future_Show_list.append(data)

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "seeking_venue": artist.seeking_venue,
        "facebook_link": artist.facebook_link,
        "image_link": artist.image_link,
        "past_shows": Previus_shows_list,
        "upcoming_shows": Future_Show_list,
        "past_shows_count": len(Previus_shows_list),
        "upcoming_shows_count": len(Future_Show_list),
    }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@ app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)

    form.name.data = artist.name,
    form.genres.data = artist.genres,
    form.city.data = artist.city,
    form.state.data = artist.state,
    form.phone.data = artist.phone,
    form.website_link.data = artist.website_link,
    form.seeking_venue.data = artist.seeking_venue,
    form.seeking_description.data = artist.seeking_description,
    form.image_link.data = artist.image_link

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@ app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    try:
        artist.name = form.name.data
        artist.genres = form.genres.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.website_link = form.website_link.data
        artist.facebook_link = form.facebook_link.data
        artist.seeking_venue = form.seeking_venue.data
        artist.seeking_description = form.seeking_description.data
        artist.image_link = form.image_link.data
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))


@ app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)

    form.name.data = venue.name,
    form.genres.data = venue.genres,
    form.city.data = venue.city,
    form.state.data = venue.state,
    form.phone.data = venue.phone,
    form.website_link.data = venue.website_link,
    form.seeking_talent.data = venue.seeking_talent,
    form.seeking_description.data = venue.seeking_description,
    form.image_link.data = venue.image_link

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@ app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

    form = VenueForm()
    venue = Venue.query.get(venue_id)
    try:
        venue.name = form.name.data
        venue.genres = form.genres.data
        venue.city = form.city.data
        venue.address = form.address.data
        venue.state = form.state.data
        venue.phone = form.phone.data
        venue.website_link = form.website_link.data
        venue.facebook_link = form.facebook_link.data
        venue.seeking_talent = form.seeking_talent.data
        venue.seeking_description = form.seeking_description.data
        venue.image_link = form.image_link.data
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@ app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@ app.route('/artists/create', methods=['POST'])
def create_artist_submission():

    form = ArtistForm(request.form)
    try:
        db.session.add(Artist(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            phone=form.phone.data,
            genres=form.genres.data,
            image_link=form.image_link.data,
            facebook_link=form.facebook_link.data,
            website_link=form.website_link.data,
            seeking_venue=form.seeking_venue.data,
            seeking_description=form.seeking_description.data,
        ))
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Artist' +
              request.form['name'] + ' could not be listed')
    finally:
        db.session.close()
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@ app.route('/shows')
def shows():

    data = []
    artist = Artist.query.all()
    venue = Venue.query.all()
    shows = Show.query.filter(
        Venue.id == Show.venue_id, Artist.id == Show.artist_id)

    for show in shows:
        artistData = Artist.query.get(show.artist_id)
        venueData = Venue.query.get(show.venue_id)

        data.append({
            "venue_id": show.venue_id,
            "venue_name": venueData.name,
            "artist_id": show.artist_id,
            "artist_name": artistData.name,
            "artist_image_link": artistData.image_link,
            "start_time": str(show.start_time)
        })
    return render_template('pages/shows.html', shows=data)


@ app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@ app.route('/shows/create', methods=['POST'])
def create_show_submission():

    form = ShowForm(request.form)
    try:
        db.session.add(Show(artist_id=form.artist_id.data,
                            venue_id=form.venue_id.data,
                            start_time=form.start_time.data))
        db.session.commit()
        flash('Show was successfully listed!')
    except:

        db.session.rollback()
        flash('An error occurred. could not be listed')
    finally:
        db.session.close()
        return render_template('pages/home.html')


@ app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@ app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
