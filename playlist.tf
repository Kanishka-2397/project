resource "spotify_playlist" "myplaylist"{
    name = "myplaylist"
    tracks = ["6g3pwMsCrqV5HcxF6p99GB",
    "7MXVkk9YMctZqd1Srtv4MB" ]              
}
data "spotify_search_track" "BTS"{               
    artist = "BTS"
}
resource "spotify_playlist" "worldfav"{
    name = "worldfav"
    tracks = [data.spotify_search_track.BTS.tracks[0].id,
    data.spotify_search_track.BTS.tracks[1].id,
    data.spotify_search_track.BTS.tracks[2].id]
}
data "spotify_search_track" "BrunoMars"{
    artist = "BrunoMars"
}
resource "spotify_playlist" "famous"{
    name = "famous"
    tracks = [data.spotify_search_track.BrunoMars.tracks[0].id,
    data.spotify_search_track.BrunoMars.tracks[1].id,
    data.spotify_search_track.BrunoMars.tracks[2].id]
}
data "spotify_search_track" "BLACKPINK"{
    artist = "BLACKPINK"
}
resource "spotify_playlist" "pop"{
    name = "pop"
    tracks = [data.spotify_search_track.BLACKPINK.tracks[0].id,
    data.spotify_search_track.BLACKPINK.tracks[1].id,
    data.spotify_search_track.BLACKPINK.tracks[2].id]
}
