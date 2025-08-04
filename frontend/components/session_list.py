"""
Session List Component for Tattoo Studio Management System.

This module provides the list component for displaying and managing sessions.
Extracted from sessions.py to improve modularity and keep files under 500 lines.
"""

import flet as ft
import sys
import os
from typing import List, Optional, Callable

# Add project root to path for imports
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)

from utils.logger import setup_logger

# Initialize logger
logger = setup_logger(__name__)


class SessionListComponent:
    """
    Session list component for displaying and managing sessions.

    This component provides a reusable list view for sessions with
    search, edit, and delete functionality.
    """

    def __init__(
        self, page: ft.Page, api_client, on_edit_callback: Optional[Callable[[int], None]] = None
    ):
        """
        Initialize the session list component.

        Args:
            page (ft.Page): Flet page instance
            api_client: API client for backend communication
            on_edit_callback (Callable): Callback function called when editing a session
        """
        self.page = page
        self.api_client = api_client
        self.on_edit_callback = on_edit_callback
        self.current_sessions: List[dict] = []

        # Initialize UI components
        self._init_ui_components()

        logger.info("Session list component initialized")

    def _init_ui_components(self):
        """Initialize UI components."""
        # Search field
        self.search_field = ft.TextField(
            label="Search sessions",
            hint_text="Search by client or artist name",
            prefix_icon="search",
            on_change=self.search_sessions,
        )

        # Sessions list
        self.sessions_list = ft.ListView(
            spacing=5,
            expand=True,
            auto_scroll=False,
        )

    def build(self) -> ft.Card:
        """
        Build and return the session list card.

        Returns:
            ft.Card: Session list component
        """
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text("Sessions", size=20, weight=ft.FontWeight.BOLD),
                                ft.ElevatedButton(
                                    "Refresh",
                                    on_click=self.refresh_sessions,
                                    icon="refresh",
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        self.search_field,
                        ft.Container(
                            content=self.sessions_list,
                            height=400,
                            border=ft.border.all(1, "#E0E0E0"),
                        ),
                    ]
                ),
                padding=20,
            )
        )

    def load_sessions(self):
        """Load sessions from the API and update the UI."""
        logger.info("Loading sessions from API")
        try:
            success, response = self.api_client.get_all_sessions()
            if success and response.get("success"):
                self.current_sessions = response.get("sessions", [])
                self.update_sessions_list()
                logger.info(f"Loaded {len(self.current_sessions)} sessions")
            else:
                error_msg = response.get("error", "Unknown error")
                logger.error(f"Error loading sessions: {error_msg}")
                self._show_error("Error", f"Failed to load sessions: {error_msg}")
        except Exception as e:
            logger.error(f"Error loading sessions: {e}")
            self._show_error("Error", f"Failed to load sessions: {str(e)}")

    def update_sessions_list(self):
        """Update the sessions list UI with current data."""
        self.sessions_list.controls.clear()

        if not self.current_sessions:
            self.sessions_list.controls.append(
                ft.Container(
                    content=ft.Text(
                        "No sessions found",
                        text_align=ft.TextAlign.CENTER,
                        color="#757575",
                    ),
                    alignment=ft.alignment.center,
                    padding=20,
                )
            )
        else:
            for session in self.current_sessions:
                self.sessions_list.controls.append(self._create_session_tile(session))

        self.sessions_list.update()

    def _create_session_tile(self, session: dict) -> ft.ListTile:
        """Create a list tile for a session."""
        status = session.get("status", "unknown")
        status_colors = {
            "scheduled": "#1E88E5",
            "in_progress": "#FB8C00",
            "completed": "#43A047",
            "cancelled": "#E53935",
        }
        status_color = status_colors.get(status, "#757575")

        return ft.ListTile(
            leading=ft.Icon("event", color="#43A047"),
            title=ft.Text(
                f"{session.get('client_name', 'Unknown')} → {session.get('artist_name', 'Unknown')}",
                weight=ft.FontWeight.BOLD,
            ),
            subtitle=ft.Column(
                [
                    ft.Text(f"Date: {session.get('session_date', 'N/A')}"),
                    ft.Text(f"Duration: {session.get('duration', 0)} hours"),
                    ft.Text(f"Price: ${session.get('price', 0):.2f}"),
                    ft.Text(f"Status: {status.title()}", color=status_color),
                    ft.Text(
                        f"Description: {session.get('description', 'N/A')[:50]}...",
                        size=11,
                        color="#757575",
                    ),
                ],
                spacing=2,
            ),
            trailing=ft.Row(
                [
                    ft.IconButton(
                        icon="edit",
                        tooltip="Edit session",
                        on_click=lambda e, sid=session["id"]: self.edit_session(sid),
                    ),
                    ft.IconButton(
                        icon="delete",
                        tooltip="Delete session",
                        icon_color="#EF5350",
                        on_click=lambda e, sid=session[
                            "id"
                        ]: self.delete_session_confirm(sid),
                    ),
                ],
                tight=True,
            ),
        )

    def edit_session(self, session_id: int):
        """Handle session edit request."""
        if self.on_edit_callback:
            self.on_edit_callback(session_id)

    def delete_session_confirm(self, session_id: int):
        """Show confirmation dialog for session deletion."""

        def on_confirm(e):
            try:
                success, response = self.api_client.delete_session(session_id)
                if success and response.get("success"):
                    self._show_success("Session deleted successfully.")
                    self.load_sessions()
                else:
                    error_msg = response.get("error", "Failed to delete session.")
                    self._show_error("Error", error_msg)
            except Exception as ex:
                logger.error(f"Error deleting session: {ex}")
                self._show_error("Error", f"Failed to delete session: {str(ex)}")
            self._close_dialog()

        def on_cancel(e):
            self._close_dialog()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm Deletion"),
            content=ft.Text("Are you sure you want to delete this session?"),
            actions=[
                ft.TextButton("Yes", on_click=on_confirm),
                ft.TextButton("No", on_click=on_cancel),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def search_sessions(self, e):
        """Search sessions based on the search field value."""
        query = (self.search_field.value or "").strip().lower()

        if not query:
            # If no search query, show all sessions
            self.update_sessions_list()
            return

        try:
            success, response = self.api_client.search_session(query)
            if success and response.get("success"):
                self.current_sessions = response.get("sessions", [])
                self.update_sessions_list()
            else:
                error_msg = response.get("error", "No sessions found.")
                self._show_error("Error", error_msg)
        except Exception as ex:
            logger.error(f"Error searching sessions: {ex}")
            self._show_error("Error", f"Failed to search sessions: {str(ex)}")

    def refresh_sessions(self, e):
        """Refresh the sessions list."""
        self.load_sessions()

    def _show_error(self, title: str, message: str):
        """Show error dialog."""
        self._show_dialog(title, message, "#EF5350")

    def _show_success(self, message: str):
        """Show success message."""
        self._show_dialog("Success", message, "#43A047")

    def _show_dialog(self, title: str, message: str, text_color: str):
        """Show a dialog with the given title, message and color."""
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(message, color=text_color),
            actions=[ft.TextButton("OK", on_click=lambda e: self._close_dialog())],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def _close_dialog(self):
        """Close the current dialog."""
        if self.page.overlay:
            dialog = self.page.overlay[-1]
            if isinstance(dialog, ft.AlertDialog):
                dialog.open = False
            self.page.overlay.pop()
            self.page.update()
