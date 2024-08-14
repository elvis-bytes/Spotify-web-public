import os

from flask import Flask, session, url_for, redirect, request, render_template

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)

client_id = os.getenv('SPOTIPY_CLIENT_ID')
client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI')
scope = 'playlist-read-private,ugc-image-upload,streaming,user-top-read,user-read-recently-played,user-library-modify,user-library-read'

cache_handler = FlaskSessionCacheHandler(session)
sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    cache_handler=cache_handler,
    show_dialog=True
)
sp = Spotify(auth_manager=sp_oauth)

@app.route('/')
def home():  #check if they've logged in
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    #return redirect(url_for('get_top_tracks')) #redirect(url_for('get_playlists')),
    return render_template('index.html')

@app.route('/callback')
def callback():
    sp_oauth.get_access_token(request.args['code'])
    return redirect(url_for('get_playlists')) #redirect(url_for('get_top_tracks'))  #

@app.route('/get_playlists')
def get_playlists():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

    playlists = sp.current_user_playlists()
    playlists_info = [(pl['name'], pl['external_urls']['spotify'])for pl in playlists['items']]
    #playlists_html = '<br>' .join([f'{name}: {url}' for name, url in playlists_info])

    top_tracks = sp.current_user_top_tracks(limit=5)
    top_tracks_info = [(track['name'], track['artists'][0]['name']) for track in top_tracks['items']]
    #top_tracks_html = '<br>'.join([f'{name} - {artist}' for name, artist in top_tracks_info])

    return render_template('index.html',playlists=playlists_info, top_tracks=top_tracks_info)#playlists_html

@app.route('/get_top_tracks')
def get_top_tracks():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

    top_tracks = sp.current_user_top_tracks(limit=5)
    top_tracks_info = [(track['name'], track['artists'][0]['name']) for track in top_tracks['items']]
    top_tracks_html = '<br>' .join([f'{name} - {artist}' for name, artist in top_tracks_info])

    return top_tracks_html

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
