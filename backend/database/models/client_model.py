"""
Client model and CRUD operations.
"""

from sqlalchemy import Column, String, Integer
from .base import Base, get_session
from utils.logger import setup_logger

logger = setup_logger(__name__)


class Client(Base):
    """Client model for storing customer information."""

    __tablename__ = "clients"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", String(100), nullable=False)
    phone = Column("phone", String(20), nullable=True)
    address = Column("address", String(200), nullable=True)
    allergies = Column("allergies", String(500), nullable=True)
    medical_info = Column("medical_info", String(1000), nullable=True)
    qr_id = Column("qr_id", String(100), nullable=True, unique=True)

    def __init__(
        self,
        name,
        phone=None,
        address=None,
        allergies=None,
        medical_info=None,
        qr_id=None,
    ):
        """
        Initialize a new Client.

        Args:
            name (str): Client's full name
            phone (str, optional): Phone number. Defaults to None.
            address (str, optional): Address. Defaults to None.
            allergies (str, optional): Known allergies. Defaults to None.
            medical_info (str, optional): Relevant medical info. Defaults to None.
            qr_id (str, optional): Unique ID for QR code. Defaults to None.
        """
        self.name = name
        self.phone = phone
        self.address = address
        self.allergies = allergies
        self.medical_info = medical_info
        self.qr_id = qr_id

    def __repr__(self):
        return f"<Client(id={self.id}, name='{self.name}')>"


# CRUD operations for Client
def create_client(
    name, phone=None, address=None, allergies=None, medical_info=None, qr_id=None
):
    """
    Create a new client.

    Args:
        name (str): Client's full name
        phone (str, optional): Phone number.
        address (str, optional): Address.
        allergies (str, optional): Known allergies.
        medical_info (str, optional): Relevant medical info.
        qr_id (str, optional): Unique ID for QR code.

    Returns:
        Client: The created client object
    """
    session = get_session()
    try:
        client = Client(
            name=name,
            phone=phone,
            address=address,
            allergies=allergies,
            medical_info=medical_info,
            qr_id=qr_id,
        )
        session.add(client)
        session.commit()
        logger.info(f"Client created successfully: {client.name}")
        return client
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating client: {e}")
        raise
    finally:
        session.close()


def read_client(client_id):
    """
    Read a client by ID.

    Args:
        client_id (int): The client's ID

    Returns:
        Client: The client object or None if not found
    """
    session = get_session()
    try:
        client = session.query(Client).filter_by(id=client_id).first()
        if client:
            logger.info(f"Client found: {client.name}")
        else:
            logger.warning(f"Client with ID {client_id} not found")
        return client
    except Exception as e:
        logger.error(f"Error reading client: {e}")
        raise
    finally:
        session.close()


def update_client(client_id, **kwargs):
    """
    Update a client's information.

    Args:
        client_id (int): The client's ID
        **kwargs: Fields to update

    Returns:
        Client: The updated client object or None if not found
    """
    session = get_session()
    try:
        client = session.query(Client).filter_by(id=client_id).first()
        if client:
            for key, value in kwargs.items():
                if hasattr(client, key):
                    setattr(client, key, value)
            session.commit()
            logger.info(f"Client updated successfully: {client.name}")
            return client
        else:
            logger.warning(f"Client with ID {client_id} not found for update")
            return None
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating client: {e}")
        raise
    finally:
        session.close()


def delete_client(client_id):
    """
    Delete a client by ID.

    Args:
        client_id (int): The client's ID

    Returns:
        bool: True if deleted successfully, False if not found
    """
    session = get_session()
    try:
        client = session.query(Client).filter_by(id=client_id).first()
        if client:
            session.delete(client)
            session.commit()
            logger.info(f"Client deleted successfully: {client.name}")
            return True
        else:
            logger.warning(f"Client with ID {client_id} not found for deletion")
            return False
    except Exception as e:
        session.rollback()
        logger.error(f"Error deleting client: {e}")
        raise
    finally:
        session.close()


def list_all_clients():
    """
    List all clients in the database.

    Returns:
        list: List of Client objects
    """
    session = get_session()
    try:
        clients = session.query(Client).all()
        logger.info(f"Retrieved {len(clients)} clients from database")
        return clients
    except Exception as e:
        logger.error(f"Error listing clients: {e}")
        raise
    finally:
        session.close()
