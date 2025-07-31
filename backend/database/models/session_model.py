"""
Session model and CRUD operations.
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from .base import Base, session
from utils.logger import setup_logger

logger = setup_logger(__name__)


class Session(Base):
    """Session model for storing tattoo session information."""

    __tablename__ = "sessions"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=False)
    date = Column("date", DateTime, nullable=False)
    status = Column("status", String(50), default="planned")
    notes = Column("notes", String(1000), nullable=True)

    def __init__(self, client_id, artist_id, date, status="planned", notes=None):
        """
        Initialize a new Session.

        Args:
            client_id (int): ID of the client.
            artist_id (int): ID of the artist.
            date (datetime): Date and time of the session.
            status (str, optional): Status of the session. Defaults to 'planned'.
            notes (str, optional): Notes about the session. Defaults to None.
        """
        self.client_id = client_id
        self.artist_id = artist_id
        self.date = date
        self.status = status
        self.notes = notes

    def __repr__(self):
        return f"<Session(id={self.id}, client_id={self.client_id}, artist_id={self.artist_id}, date='{self.date}')>"


# CRUD operations for Session
def create_session(client_id, artist_id, date, status="planned", notes=None):
    """
    Create a new session.

    Args:
        client_id (int): ID of the client.
        artist_id (int): ID of the artist.
        date (datetime): Date and time of the session.
        status (str, optional): Status of the session.
        notes (str, optional): Notes about the session.

    Returns:
        Session: The created session object
    """
    try:
        session_obj = Session(
            client_id=client_id,
            artist_id=artist_id,
            date=date,
            status=status,
            notes=notes,
        )
        session.add(session_obj)
        session.commit()
        logger.info(
            f"Session created successfully for client {client_id} with artist {artist_id}"
        )
        return session_obj
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating session: {e}")
        raise


def read_session(session_id):
    """
    Read a session by ID.

    Args:
        session_id (int): The session's ID

    Returns:
        Session: The session object or None if not found
    """
    try:
        session_obj = session.query(Session).filter_by(id=session_id).first()
        if session_obj:
            logger.info(f"Session found: {session_obj.id}")
        else:
            logger.warning(f"Session with ID {session_id} not found")
        return session_obj
    except Exception as e:
        logger.error(f"Error reading session: {e}")
        raise


def update_session(session_id, **kwargs):
    """
    Update a session's information.

    Args:
        session_id (int): The session's ID
        **kwargs: Fields to update

    Returns:
        Session: The updated session object or None if not found
    """
    try:
        session_obj = session.query(Session).filter_by(id=session_id).first()
        if session_obj:
            for key, value in kwargs.items():
                if hasattr(session_obj, key):
                    setattr(session_obj, key, value)
            session.commit()
            logger.info(f"Session updated successfully: {session_obj.id}")
            return session_obj
        else:
            logger.warning(f"Session with ID {session_id} not found for update")
            return None
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating session: {e}")
        raise


def delete_session(session_id):
    """
    Delete a session by ID.

    Args:
        session_id (int): The session's ID

    Returns:
        bool: True if deleted successfully, False if not found
    """
    try:
        session_obj = session.query(Session).filter_by(id=session_id).first()
        if session_obj:
            session.delete(session_obj)
            session.commit()
            logger.info(f"Session deleted successfully: {session_obj.id}")
            return True
        else:
            logger.warning(f"Session with ID {session_id} not found for deletion")
            return False
    except Exception as e:
        session.rollback()
        logger.error(f"Error deleting session: {e}")
        raise


def list_all_sessions():
    """
    List all sessions in the database.

    Returns:
        list: List of Session objects
    """
    try:
        sessions = session.query(Session).all()
        logger.info(f"Retrieved {len(sessions)} sessions from database")
        return sessions
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise
