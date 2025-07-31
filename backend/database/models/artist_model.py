"""
Artist model and CRUD operations.
"""

from sqlalchemy import Column, String, Integer
from .base import Base, get_session
from utils.logger import setup_logger

logger = setup_logger(__name__)


class Artist(Base):
    """Artist model for storing artist information."""

    __tablename__ = "artists"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", String(100), nullable=False)
    phone = Column("phone", String(20), nullable=True)
    email = Column("email", String(100), nullable=True, unique=True)
    bio = Column("bio", String(1000), nullable=True)
    portfolio = Column("portfolio", String(500), nullable=True)

    def __init__(self, name, phone=None, email=None, bio=None, portfolio=None):
        """
        Initialize a new Artist.

        Args:
            name (str): Artist's full name
            phone (str, optional): Phone number. Defaults to None.
            email (str, optional): Email address. Defaults to None.
            bio (str, optional): Artist's biography. Defaults to None.
            portfolio (str, optional): Link or path to portfolio. Defaults to None.
        """
        self.name = name
        self.phone = phone
        self.email = email
        self.bio = bio
        self.portfolio = portfolio

    def __repr__(self):
        return f"<Artist(id={self.id}, name='{self.name}')>"


# CRUD operations for Artist
def create_artist(name, phone=None, email=None, bio=None, portfolio=None):
    """
    Create a new artist.

    Args:
        name (str): Artist's full name
        phone (str, optional): Phone number.
        email (str, optional): Email address.
        bio (str, optional): Artist's biography.
        portfolio (str, optional): Link or path to portfolio.

    Returns:
        Artist: The created artist object
    """
    session = get_session()
    try:
        artist = Artist(
            name=name, phone=phone, email=email, bio=bio, portfolio=portfolio
        )
        session.add(artist)
        session.commit()
        logger.info(f"Artist created successfully: {artist.name}")
        return artist
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating artist: {e}")
        raise
    finally:
        session.close()


def read_artist(artist_id):
    """
    Read an artist by ID.

    Args:
        artist_id (int): The artist's ID

    Returns:
        Artist: The artist object or None if not found
    """
    session = get_session()
    try:
        artist = session.query(Artist).filter_by(id=artist_id).first()
        if artist:
            logger.info(f"Artist found: {artist.name}")
        else:
            logger.warning(f"Artist with ID {artist_id} not found")
        return artist
    except Exception as e:
        logger.error(f"Error reading artist: {e}")
        raise
    finally:
        session.close()


def update_artist(artist_id, **kwargs):
    """
    Update an artist's information.

    Args:
        artist_id (int): The artist's ID
        **kwargs: Fields to update

    Returns:
        Artist: The updated artist object or None if not found
    """
    session = get_session()
    try:
        artist = session.query(Artist).filter_by(id=artist_id).first()
        if artist:
            for key, value in kwargs.items():
                if hasattr(artist, key):
                    setattr(artist, key, value)
            session.commit()
            logger.info(f"Artist updated successfully: {artist.name}")
            return artist
        else:
            logger.warning(f"Artist with ID {artist_id} not found for update")
            return None
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating artist: {e}")
        raise
    finally:
        session.close()


def delete_artist(artist_id):
    """
    Delete an artist by ID.

    Args:
        artist_id (int): The artist's ID

    Returns:
        bool: True if deleted successfully, False if not found
    """
    session = get_session()
    try:
        artist = session.query(Artist).filter_by(id=artist_id).first()
        if artist:
            session.delete(artist)
            session.commit()
            logger.info(f"Artist deleted successfully: {artist.name}")
            return True
        else:
            logger.warning(f"Artist with ID {artist_id} not found for deletion")
            return False
    except Exception as e:
        session.rollback()
        logger.error(f"Error deleting artist: {e}")
        raise
    finally:
        session.close()


def list_all_artists():
    """
    List all artists in the database.

    Returns:
        list: List of Artist objects
    """
    session = get_session()
    try:
        artists = session.query(Artist).all()
        logger.info(f"Retrieved {len(artists)} artists from database")
        return artists
    except Exception as e:
        logger.error(f"Error listing artists: {e}")
        raise
    finally:
        session.close()
