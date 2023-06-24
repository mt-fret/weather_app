import sys
import os

from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone, timedelta

from open_weather_api import get_weather, get_city
from keys import flask_secret_key


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///"+os.path.join(basedir, "weather.db")
app.secret_key = flask_secret_key
db = SQLAlchemy(app)


class City(db.Model):
    """
    Stores information on names of cities
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return '<city %r>' % self.name


@app.route('/')
def index():
    """
    Renders an HTML with weather information on each city in DB
    :return: rendered HTML
    """
    cities = City.query.all()
    cities_list = []
    if len(cities) > 6:
        db.session.delete(City.query.first())
        db.session.commit()
        cities = City.query.all()
    for cit in cities:
        dict_with_weather_info = get_weather(cit.name)
        if dict_with_weather_info is not None:
            dict_with_weather_info['id'] = cit.id
            city_hour = datetime.now(timezone.utc) + timedelta(seconds=dict_with_weather_info['timezone'])
            dict_with_weather_info['hour'] = city_hour.hour
            dict_with_weather_info['time'] = city_hour.time().isoformat(timespec='minutes')
            cities_list.append(dict_with_weather_info)

    return render_template('index.html', cities=cities_list)


@app.route('/add', methods=['POST', 'GET'])
def add_city():
    """
    Adds city to DB and redirects to main page
    :return: redirect to main page
    """
    try:
        r = request.form.get('city_name')
        city_to_check = get_city(r)
        if city_to_check is None:
            flash("The city doesn't exist!")
            return redirect('/')
        for cit in City.query.all():
            if r.lower() == cit.name.lower():
                flash('The city has already been added to the list!')
                return redirect('/')
        cit = City(name=r)
        db.session.add(cit)
        db.session.commit()
        return redirect('/')
    except KeyError:
        return render_template('index.html')


@app.route('/delete/<city_id>', methods=['GET', 'POST'])
def delete(city_id):
    """
    Deletes a city from DB based on ID
    :param city_id:
    :return: redirect to main page
    """
    city_to_delete = City.query.filter_by(id=city_id).first()
    db.session.delete(city_to_delete)
    db.session.commit()
    return redirect('/')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        with app.app_context():
            db.create_all()
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        with app.app_context():
            db.create_all()
        app.run(port=8000, debug=True)
