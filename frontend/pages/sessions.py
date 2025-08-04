"""
Session Management Page for Tattoo Studio Management System.

This module provides the user interface for managing tattoo sessions.
Refactored into smaller components to improve modularity and maintainability.

Key Features:
- Session creation and editing using SessionFormComponent
- Session listing and management using SessionListComponent
- Search functionality
- Integration with backend API
"""

import flet as ft
import sys
import os
from datetime import datetime

# Add project root to path for imports
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)

from frontend.utils.api_client import get_api_client
from frontend.components.session_form import SessionFormComponent
from frontend.components.session_list import SessionListComponent
from utils.logger import setup_logger

# Initialize logger
logger = setup_logger(__name__)


class SessionManagementPage:
    """
    Session management page component for the Flet application.

    Provides a complete interface for CRUD operations on sessions,
    using modular components for better code organization.
    """

    def __init__(self, page: ft.Page):
        """
        Initialize the session management page.

        Args:
            page (ft.Page): Flet page instance
        """
        self.page = page
        self.api_client = get_api_client()

        # Initialize components
        self.form_component = SessionFormComponent(
            page=page,
            api_client=self.api_client,
            on_save_callback=self._on_session_saved,
        )

        self.list_component = SessionListComponent(
            page=page,
            api_client=self.api_client,
            on_edit_callback=self._on_edit_session,
        )

        # Add date picker to page overlay for form component
        if self.form_component.session_date not in page.overlay:
            page.overlay.append(self.form_component.session_date)

        logger.info("Session management page initialized")

    def build(self) -> ft.View:
        """
        Build and return the session management page view.

        Returns:
            ft.View: Complete session management page
        """
        # Main layout with form and list components
        content = ft.Row(
            [
                ft.Container(
                    content=self.form_component.build(),
                    width=400,
                    expand=False,
                ),
                ft.Container(
                    content=self.list_component.build(),
                    expand=True,
                ),
            ],
            spacing=20,
            expand=True,
        )

        return ft.View(
            route="/sessions",
            controls=[
                ft.Container(
                    content=content,
                    padding=20,
                    expand=True,
                )
            ],
        )

    def _on_session_saved(self):
        """Callback called when a session is successfully saved."""
        # Refresh the session list
        self.list_component.load_sessions()

    def _on_edit_session(self, session_id: int):
        """Callback called when a session edit is requested."""
        # Load session data into the form for editing
        self.form_component.load_session_for_edit(session_id)

    def initialize_page(self):
        """Initialize the page by loading data."""
        # Load dropdown data for the form
        self.form_component.load_dropdown_data()

        # Load the initial session list
        self.list_component.load_sessions()

        logger.info("Session management page data loaded")
