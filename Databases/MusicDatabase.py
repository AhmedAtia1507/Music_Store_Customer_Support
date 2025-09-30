import sqlite3 # Standard Python library for SQLite database interaction
import requests # Library for making HTTP requests (to download the SQL script)
from langchain_community.utilities.sql_database import SQLDatabase # LangChain utility to interact with SQL databases
from sqlalchemy import create_engine, text # SQLAlchemy function to create a database engine
from sqlalchemy.pool import StaticPool # SQLAlchemy connection pool class for in-memory databases
from langchain_core.tools import tool # LangChain decorator to define tools

class MusicDatabase:
    """Class to represent a music database."""
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if not self.__initialized:
            print("Initializing MusicDatabase...")
            self.db_engine = None
            self.db = None
            self.get_chinook_db()
            self.__initialized = True

    def get_chinook_db(self):
        """Pull sql file, populate in-memory database, and create engine.""" # URL to the raw SQL script for the Chinook database
        try:
            url = "https://raw.githubusercontent.com/lerocha/chinook-database/master/ChinookDatabase/DataSources/Chinook_Sqlite.sql"

            # Fetch the SQL script content from the URL 
            response = requests.get(url)

            # Create an in-memory SQLite database connection.
            connection = sqlite3.connect(":memory:", check_same_thread=False)

            # Execute the SQL script to populate the in-memory database with Chinook data
            connection.executescript(response.text)

            # Create a SQLAlchemy engine for the in-memory SQLite database.
            # `creator=lambda: connection` tells SQLAlchemy how to get a new connection.
            # `poolclass=StaticPool` is used for in-memory databases, ensuring the same
            # connection is reused.
            # `connect_args` are passed directly to the `sqlite3.connect` function.
            self.db_engine = create_engine(
                "sqlite://", # SQLite in-memory database URL
                creator=lambda: connection,
                poolclass=StaticPool,
                connect_args={"check_same_thread": False},
            )
            self.db = SQLDatabase(self.db_engine)
        except Exception as e:
            print(f"Error setting up the database: {e}")
    
    def get_albums_by_artist(self, artist_name: str) -> list[dict]:
        """Get albums by a specific artist."""
        if not self.db_engine:
            raise RuntimeError("DB engine not initialized")
        query = """
        SELECT Album.Title AS album_title, Artist.Name AS artist_name
        FROM Album
        JOIN Artist ON Album.ArtistId = Artist.ArtistId
        WHERE Artist.Name = :artist_name
        LIMIT 5;
        """
        with self.db_engine.connect() as conn:
            res = conn.execute(text(query), {"artist_name": artist_name})
            return [dict(row._mapping) for row in res]
    
    def get_tracks_by_artist(self, artist_name: str) -> list[dict]:
        """Get tracks by a specific artist."""
        if not self.db_engine:
            raise RuntimeError("DB engine not initialized")
        query = """
        SELECT Track.Name AS track_name, Album.Title AS album_title, Artist.Name AS artist_name
        FROM Track
        JOIN Album ON Track.AlbumId = Album.AlbumId
        JOIN Artist ON Album.ArtistId = Artist.ArtistId
        WHERE Artist.Name = :artist_name
        LIMIT 5;
        """
        with self.db_engine.connect() as conn:
            res = conn.execute(text(query), {"artist_name": artist_name})
            return [dict(row._mapping) for row in res]
    
    def get_songs_by_genre(self, genre_name: str) -> list[dict]:
        """Get songs by a specific genre."""
        if not self.db_engine:
            raise RuntimeError("DB engine not initialized")
        query = """
        SELECT Track.Name AS track_name, Genre.Name AS genre_name, Album.Title AS album_title, Artist.Name AS artist_name
        FROM Track
        JOIN Genre ON Track.GenreId = Genre.GenreId
        JOIN Album ON Track.AlbumId = Album.AlbumId
        JOIN Artist ON Album.ArtistId = Artist.ArtistId
        WHERE Genre.Name = :genre_name
        LIMIT 5;
        """
        with self.db_engine.connect() as conn:
            res = conn.execute(text(query), {"genre_name": genre_name})
            return [dict(row._mapping) for row in res]

    def check_for_track(self, track_name: str) -> bool:
        """Check if a track exists in the database."""
        if not self.db_engine:
            raise RuntimeError("DB engine not initialized")
        query = "SELECT 1 FROM Track WHERE Name = :track_name LIMIT 1;"
        with self.db_engine.connect() as conn:
            res = conn.execute(text(query), {"track_name": track_name})
            return res.fetchone() is not None
 
    def check_for_album(self, album_title: str) -> bool:
        """Check if an album exists in the database."""
        if not self.db_engine:
            raise RuntimeError("DB engine not initialized")
        query = "SELECT 1 FROM Album WHERE Title = :album_title LIMIT 1;"
        with self.db_engine.connect() as conn:
            res = conn.execute(text(query), {"album_title": album_title})
            return res.fetchone() is not None

    def check_for_artist(self, artist_name: str) -> bool:
        """Check if an artist exists in the database."""
        if not self.db_engine:
            raise RuntimeError("DB engine not initialized")
        query = "SELECT 1 FROM Artist WHERE Name = :artist_name LIMIT 1;"
        with self.db_engine.connect() as conn:
            res = conn.execute(text(query), {"artist_name": artist_name})
            return res.fetchone() is not None

    def get_all_artists(self) -> list[str]:
        """Get a list of all artist names in the database."""
        if not self.db_engine:
            raise RuntimeError("DB engine not initialized")
        query = "SELECT Name FROM Artist ORDER BY Name ASC LIMIT 5;"
        with self.db_engine.connect() as conn:
            res = conn.execute(text(query))
            return [row[0] for row in res.fetchall()]

    def get_all_genres(self) -> list[str]:
        """Get a list of all genre names in the database."""
        if not self.db_engine:
            raise RuntimeError("DB engine not initialized")
        query = "SELECT Name FROM Genre ORDER BY Name ASC LIMIT 5;"
        with self.db_engine.connect() as conn:
            res = conn.execute(text(query))
            return [row[0] for row in res.fetchall()]

    def get_all_albums(self) -> list[str]:
        """Get a list of all album titles in the database."""
        if not self.db_engine:
            raise RuntimeError("DB engine not initialized")
        query = "SELECT Title FROM Album ORDER BY Title ASC LIMIT 5;"
        with self.db_engine.connect() as conn:
            res = conn.execute(text(query))
            return [row[0] for row in res.fetchall()]

    def search_tracks(self, search_term: str) -> list[dict]:
        """Search for tracks by name, album title, or artist name."""
        if not self.db_engine:
            raise RuntimeError("DB engine not initialized")
        like_term = f"%{search_term}%"
        query = """
        SELECT Track.Name AS track_name, Album.Title AS album_title, Artist.Name AS artist_name
        FROM Track
        JOIN Album ON Track.AlbumId = Album.AlbumId
        JOIN Artist ON Album.ArtistId = Artist.ArtistId
        WHERE Track.Name LIKE :like_term
           OR Album.Title LIKE :like_term
           OR Artist.Name LIKE :like_term
        LIMIT 5;
        """
        with self.db_engine.connect() as conn:
            res = conn.execute(text(query), {"like_term": like_term})
            return [dict(row._mapping) for row in res]

    def search_albums(self, search_term: str) -> list[dict]:
        """Search for albums by title or artist name."""
        if not self.db_engine:
            raise RuntimeError("DB engine not initialized")
        like_term = f"%{search_term}%"
        query = """
        SELECT Album.Title AS album_title, Artist.Name AS artist_name
        FROM Album
        JOIN Artist ON Album.ArtistId = Artist.ArtistId
        WHERE Album.Title LIKE :like_term
           OR Artist.Name LIKE :like_term
        LIMIT 5;
        """
        with self.db_engine.connect() as conn:
            res = conn.execute(text(query), {"like_term": like_term})
            return [dict(row._mapping) for row in res]