const form = document.getElementById('songForm');

form.addEventListener('submit', function(event) {
    event.preventDefault();

    const songLinkInput = document.getElementById('songLink');
    const songLinkValue = songLinkInput.value;

    const regex = /^https:\/\/open\.spotify\.com\/track\/[a-zA-Z0-9]+(\?si=[a-zA-Z0-9]+)?$/;

    if (regex.test(songLinkValue)) {
        alert('Playlist Created!');
    } else {
        alert('Invalid song link format. Please enter a valid Spotify song link.');
    }
});
