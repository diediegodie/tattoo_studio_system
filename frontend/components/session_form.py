"""
Session Form Component for Tattoo Studio Management System.

This module provides the form component for creating and editing sessions.
Extracted from sessions.py to improve modularity and keep files under 500 lines.
"""

import flet as ft
import sys
import os
from typing import List, Optional, Callable
from datetime import datetime, date

# Add project root to path for imports
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)

from utils.logger import setup_logger

# Initialize logger
logger = setup_logger(__name__)


class SessionFormComponent:
    """
    Session form component for creating and editing sessions.

    This component provides a reusable form for session data entry,
    handling validation and submission to the API.
    """

    def __init__(self, page: ft.Page, api_client, on_save_callback: Optional[Callable] = None):
        """
        Initialize the session form component.

        Args:
            page (ft.Page): Flet page instance
            api_client: API client for backend communication
            on_save_callback (Optional[Callable]): Callback function called after successful save
        """
        self.page = page
        self.api_client = api_client
        self.on_save_callback = on_save_callback
        self.editing_session_id: Optional[int] = None

        # Initialize form fields
        self._init_form_fields()

        logger.info("Session form component initialized")

    def _init_form_fields(self):
        """Initialize all form input fields."""
        # Client dropdown
        self.client_dropdown = ft.Dropdown(
            label="Client",
            hint_text="Select a client",
            options=[],
        )

        # Artist dropdown
        self.artist_dropdown = ft.Dropdown(
            label="Artist",
            hint_text="Select an artist",
            options=[],
        )

        # Date picker and field
        self.session_date = ft.DatePicker(
            first_date=datetime(2020, 1, 1),
            last_date=datetime(2030, 12, 31),
            value=datetime.now(),
        )
        self.date_field = ft.TextField(
            label="Session Date",
            hint_text="YYYY-MM-DD",
            read_only=True,
            on_click=self._open_date_picker,
        )

        # Other form fields
        self.duration_field = ft.TextField(
            label="Duration (hours)",
            hint_text="e.g., 2.5",
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self.description_field = ft.TextField(
            label="Description",
            hint_text="Session description or notes",
            multiline=True,
            max_lines=3,
        )
        self.price_field = ft.TextField(
            label="Price ($)",
            hint_text="e.g., 150.00",
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self.status_dropdown = ft.Dropdown(
            label="Status",
            hint_text="Select status",
            options=[
                ft.dropdown.Option("scheduled", "Scheduled"),
                ft.dropdown.Option("in_progress", "In Progress"),
                ft.dropdown.Option("completed", "Completed"),
                ft.dropdown.Option("cancelled", "Cancelled"),
            ],
            value="scheduled",
        )

        # Set up date picker callback
        self.session_date.on_change = self._on_date_change

    def _open_date_picker(self, e=None):
        """Open the date picker dialog."""
        self.session_date.open = True
        self.page.update()

    def _on_date_change(self, e):
        """Handle date picker change."""
        if self.session_date.value:
            self.date_field.value = self.session_date.value.strftime("%Y-%m-%d")
            self.page.update()

    def build(self) -> ft.Card:
        """
        Build and return the session form card.

        Returns:
            ft.Card: Session form component
        """
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Add/Edit Session", size=20, weight=ft.FontWeight.BOLD),
                        self.client_dropdown,
                        self.artist_dropdown,
                        self.date_field,
                        self.duration_field,
                        self.description_field,
                        self.price_field,
                        self.status_dropdown,
                        ft.Row(
                            [
                                ft.ElevatedButton(
                                    "Save Session",
                                    on_click=self.save_session,
                                    icon="save",
                                ),
                                ft.OutlinedButton(
                                    "Cancel", on_click=self.cancel_edit, icon="cancel"
                                ),
                            ]
                        ),
                    ]
                ),
                padding=20,
            )
        )

    def load_dropdown_data(self):
        """Load clients and artists data for dropdowns."""
        try:
            # Load clients
            success, client_response = self.api_client.get_all_clients()
            if success and client_response.get("success"):
                clients = client_response.get("clients", [])
                self.client_dropdown.options = [
                    ft.dropdown.Option(str(client["id"]), client["name"])
                    for client in clients
                ]
            else:
                logger.warning("Failed to load clients for dropdown")

            # Load artists
            success, artist_response = self.api_client.get_all_artists()
            if success and artist_response.get("success"):
                artists = artist_response.get("artists", [])
                self.artist_dropdown.options = [
                    ft.dropdown.Option(str(artist["id"]), artist["name"])
                    for artist in artists
                ]
            else:
                logger.warning("Failed to load artists for dropdown")

            self.page.update()
        except Exception as e:
            logger.error(f"Error loading dropdown data: {e}")

    def save_session(self, e):
        """Save session data (create or update)."""
        # Get form values
        client_id = self.client_dropdown.value
        artist_id = self.artist_dropdown.value
        session_date = self.date_field.value
        duration = self.duration_field.value
        description = self.description_field.value
        price = self.price_field.value
        status = self.status_dropdown.value

        # Basic validation
        if (
            not client_id
            or not artist_id
            or not session_date
            or not duration
            or not price
            or not status
        ):
            self._show_error(
                "Validation Error", "All fields except description are required."
            )
            return

        try:
            duration_val = float(duration)
            price_val = float(price)
        except ValueError:
            self._show_error("Validation Error", "Duration and price must be numbers.")
            return

        try:
            if self.editing_session_id:
                # Update existing session
                success, response = self.api_client.update_session(
                    session_id=self.editing_session_id,
                    client_id=int(client_id),
                    artist_id=int(artist_id),
                    session_date=session_date,
                    duration=duration_val,
                    description=description,
                    price=price_val,
                    status=status,
                )
                if success and response.get("success"):
                    self._show_success("Session updated successfully.")
                    self.editing_session_id = None
                else:
                    error_msg = response.get("error", "Failed to update session.")
                    self._show_error("Error", error_msg)
            else:
                # Create new session
                success, response = self.api_client.create_session(
                    client_id=int(client_id),
                    artist_id=int(artist_id),
                    session_date=session_date,
                    duration=duration_val,
                    description=description,
                    price=price_val,
                    status=status,
                )
                if success and response.get("success"):
                    self._show_success("Session created successfully.")
                else:
                    error_msg = response.get("error", "Failed to create session.")
                    self._show_error("Error", error_msg)

            # Call callback if provided
            if self.on_save_callback:
                self.on_save_callback()

            self.clear_form()
        except Exception as ex:
            logger.error(f"Error saving session: {ex}")
            self._show_error("Error", f"Failed to save session: {str(ex)}")

    def load_session_for_edit(self, session_id: int):
        """Load session data for editing."""
        logger.info(f"Loading session {session_id} for editing")
        try:
            success, response = self.api_client.get_session(session_id)
            if success and response.get("success"):
                session = response.get("session", {})
                self.client_dropdown.value = str(session.get("client_id", ""))
                self.artist_dropdown.value = str(session.get("artist_id", ""))
                self.date_field.value = session.get("session_date", "")
                self.duration_field.value = str(session.get("duration", ""))
                self.description_field.value = session.get("description", "")
                self.price_field.value = str(session.get("price", ""))
                self.status_dropdown.value = session.get("status", "scheduled")
                self.editing_session_id = session_id
                self.page.update()
            else:
                error_msg = response.get("error", "Session not found.")
                self._show_error("Error", error_msg)
        except Exception as ex:
            logger.error(f"Error loading session for edit: {ex}")
            self._show_error("Error", f"Failed to load session: {str(ex)}")

    def cancel_edit(self, e):
        """Cancel editing and clear form."""
        self.clear_form()
        self.editing_session_id = None

    def clear_form(self):
        """Clear all form fields."""
        self.client_dropdown.value = None
        self.artist_dropdown.value = None
        self.date_field.value = ""
        self.duration_field.value = ""
        self.description_field.value = ""
        self.price_field.value = ""
        self.status_dropdown.value = "scheduled"
        self.page.update()

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
