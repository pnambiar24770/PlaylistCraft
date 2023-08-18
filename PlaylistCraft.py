from flask import Flask, render_template, request
import os
import dotenv
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import re

app = Flask(__name__,static_folder="static")
app.secret_key = os.urandom(24)

# load environment variables from secrets.env file
load_dotenv("secrets.env")

# Spotify OAuth setup
sp_oauth = SpotifyOAuth(
    os.environ.get("SPOTIFY_CLIENT_ID"),
    os.environ.get("SPOTIFY_CLIENT_SECRET"),
    os.environ.get("SPOTIFY_REDIRECT_URI"),
    os.environ.get("SPOTIFY_USER"),
    scope="playlist-modify-public"
)

# initialize Spotipy with OAuth
spotifyObject = spotipy.Spotify(auth_manager=sp_oauth)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        song_link = request.form.get('songLink')
        count = request.form.get('count')
        regex = r'^https:\/\/open\.spotify\.com\/track\/([a-zA-Z0-9]+)(\?si=[a-zA-Z0-9]+)?$'

        if re.match(regex, song_link):
            match = re.match(regex, song_link)
            song_uri = match.group(1)

            # get song details
            seed_song = spotifyObject.track(song_uri)
            seed_song_name = seed_song['name']
            seed_audio_features = spotifyObject.audio_features(song_uri)[0]
            target_danceability = seed_audio_features['danceability']
            target_energy = seed_audio_features['energy']
            target_loudness = seed_audio_features['loudness']
            target_tempo = seed_audio_features['tempo']
            target_key = seed_audio_features['key']

            # get recommendations
            recommendations = spotifyObject.recommendations(seed_tracks=[song_uri], limit=int(count),
                                                            target_danceability=target_danceability,
                                                            target_energy=target_energy,
                                                            target_loudness=target_loudness,
                                                            target_tempo=target_tempo,
                                                            target_key=target_key)

            # create playlist
            playlist_name = f"Similar Tracks to {seed_song_name}"
            playlist_description = f"Playlist containing tracks similar to {seed_song_name}"
            playlist = spotifyObject.user_playlist_create(user=os.environ.get("SPOTIFY_USER"),
                                                          name=playlist_name, public=True, description=playlist_description)
            playlist_id = playlist['id']

            # add tracks to the playlist
            track_uris = [track['uri'] for track in recommendations['tracks']]
            spotifyObject.user_playlist_add_tracks(user=os.environ.get("SPOTIFY_USER"),
                                                   playlist_id=playlist_id, tracks=track_uris)

            return f"Playlist '{playlist_name}' with {len(track_uris)} similar tracks has been created."
        else:
            return "Invalid song link format. Please enter a valid Spotify song link."

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
