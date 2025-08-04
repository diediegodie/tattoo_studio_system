"""
Artist Management Page for Tattoo Studio Management System.

This module provides the user interface for managing tattoo artists including:
- Displaying list of all artists
- Creating new artists
- Editing existing artists
- Deleting artists
- Searching artists by name

Uses the API client to communicate with the Flask backend.
"""

import flet as ft
import sys
import os
from typing import List, Optional

# Add project root to path for imports
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)

from frontend.utils.api_client import get_api_client
from utils.logger import setup_logger

# Initialize logger
logger = setup_logger(__name__)


class ArtistManagementPage:
    """
    Artist management page component for the Flet application.

    Provides a complete interface for CRUD operations on artists,
    connected to the Flask backend API.
    """

    def __init__(self, page: ft.Page):
        """
        Initialize the artist management page.

        Args:
            page (ft.Page): Flet page instance
        """
        self.page = page
        self.api_client = get_api_client()

        # UI components
        self.artists_list = ft.ListView()
        self.search_field = ft.TextField(
            label="Search by name", on_submit=self.search_artist, suffix_icon="search"
        )
        self.name_field = ft.TextField(label="Name", hint_text="Enter artist name")
        self.specialties_field = ft.TextField(
            label="Specialties", hint_text="e.g., Traditional, Realism, Portraits"
        )
        self.experience_field = ft.TextField(
            label="Years of Experience",
            hint_text="e.g., 5",
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self.hourly_rate_field = ft.TextField(
            label="Hourly Rate",
            hint_text="e.g., 150.00",
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self.bio_field = ft.TextField(
            label="Bio (optional)",
            hint_text="Artist biography...",
            multiline=True,
            max_lines=3,
        )
        self.active_checkbox = ft.Checkbox(label="Active", value=True)

        # State
        self.current_artists: List[dict] = []
        self.editing_artist_id: Optional[int] = None

        logger.info("Artist management page initialized")

    def build(self) -> ft.View:
        """
        Build and return the artist management page view.

        Returns:
            ft.View: Complete artist management page
        """
        # Create form for adding/editing artists
        artist_form = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Add/Edit Artist", size=20, weight=ft.FontWeight.BOLD),
                        self.name_field,
                        self.specialties_field,
                        self.experience_field,
                        self.hourly_rate_field,
                        self.bio_field,
                        self.active_checkbox,
                        ft.Row(
                            [
                                ft.ElevatedButton(
                                    "Save Artist",
                                    on_click=self.save_artist,
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

        # Create artist list section
        artist_list_section = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text("Artists", size=20, weight=ft.FontWeight.BOLD),
                                ft.ElevatedButton(
                                    "Refresh",
                                    on_click=self.refresh_artists,
                                    icon="refresh",
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        self.search_field,
                        ft.Container(
                            content=self.artists_list,
                            height=400,
                            border=ft.border.all(1, "#E0E0E0"),
                        ),
                    ]
                ),
                padding=20,
            )
        )

        # Main layout
        content = ft.Row(
            [
                ft.Container(
                    content=artist_form,
                    width=400,
                    expand=False,
                ),
                ft.Container(
                    content=artist_list_section,
                    expand=True,
                ),
            ],
            spacing=20,
            expand=True,
        )

        return ft.View(
            route="/artists",
            controls=[
                ft.Container(
                    content=content,
                    padding=20,
                    expand=True,
                )
            ],
        )

    def load_artists(self):
        """Load artists from the API and update the UI."""
        logger.info("Loading artists from API")
        try:
            success, response = self.api_client.list_artists()
            if success and response.get("success"):
                self.current_artists = response.get("artists", [])
                self.update_artists_list()
                logger.info(f"Loaded {len(self.current_artists)} artists")
            else:
                error_msg = response.get("error", "Unknown error")
                logger.error(f"Error loading artists: {error_msg}")
                self.show_error("Error", f"Failed to load artists: {error_msg}")
        except Exception as e:
            logger.error(f"Error loading artists: {e}")
            self.show_error("Error", f"Failed to load artists: {str(e)}")

    def update_artists_list(self):
        """Update the artists list UI with current data."""
        self.artists_list.controls.clear()

        if not self.current_artists:
            self.artists_list.controls.append(
                ft.Container(
                    content=ft.Text(
                        "No artists found",
                        text_align=ft.TextAlign.CENTER,
                        color="#757575",  # GREY_600 hex code
                    ),
                    alignment=ft.alignment.center,
                    padding=20,
                )
            )
        else:
            for artist in self.current_artists:
                self.artists_list.controls.append(self._create_artist_tile(artist))

        self.artists_list.update()

    def _create_artist_tile(self, artist: dict) -> ft.ListTile:
        """Create a list tile for an artist."""
        status_color = (
            "#4CAF50" if artist.get("active", True) else "#F44336"
        )  # GREEN/RED hex codes
        status_text = "Active" if artist.get("active", True) else "Inactive"

        return ft.ListTile(
            leading=ft.Icon("brush", color="#8E24AA"),  # PURPLE_600 hex code
            title=ft.Text(artist.get("name", "Unknown"), weight=ft.FontWeight.BOLD),
            subtitle=ft.Column(
                [
                    ft.Text(f"Specialties: {artist.get('specialties', 'N/A')}"),
                    ft.Text(f"Experience: {artist.get('experience_years', 0)} years"),
                    ft.Text(f"Rate: ${artist.get('hourly_rate', 0):.2f}/hour"),
                    ft.Text(f"Status: {status_text}", color=status_color),
                ],
                spacing=2,
            ),
            trailing=ft.Row(
                [
                    ft.IconButton(
                        icon="edit",
                        tooltip="Edit artist",
                        on_click=lambda e, aid=artist["id"]: self.edit_artist(aid),
                    ),
                    ft.IconButton(
                        icon="delete",
                        tooltip="Delete artist",
                        icon_color="#EF5350",  # RED_400 hex code
                        on_click=lambda e, aid=artist["id"]: self.delete_artist_confirm(
                            aid
                        ),
                    ),
                ],
                tight=True,
            ),
        )

    def save_artist(self, e):
        """Save artist data (create or update)."""
        name = (self.name_field.value or "").strip()
        specialties = (self.specialties_field.value or "").strip()
        experience = (self.experience_field.value or "").strip()
        hourly_rate = (self.hourly_rate_field.value or "").strip()
        bio = (self.bio_field.value or "").strip()
        active = self.active_checkbox.value

        if not name:
            self.show_error("Validation Error", "Name is required.")
            return

        artist_data = {
            "name": name,
            "specialties": specialties,
            "experience_years": int(experience) if experience else 0,
            "hourly_rate": float(hourly_rate) if hourly_rate else 0.0,
            "bio": bio,
            "active": active,
        }

        try:
            if self.editing_artist_id:
                # Update existing artist
                success, response = self.api_client.update_artist(
                    self.editing_artist_id, **artist_data
                )
                if success and response.get("success"):
                    self.show_success("Artist updated successfully.")
                    self.editing_artist_id = None
                else:
                    error_msg = response.get("error", "Failed to update artist.")
                    self.show_error("Error", error_msg)
            else:
                # Create new artist
                success, response = self.api_client.create_artist(**artist_data)
                if success and response.get("success"):
                    self.show_success("Artist created successfully.")
                else:
                    error_msg = response.get("error", "Failed to create artist.")
                    self.show_error("Error", error_msg)
            self.load_artists()
            self.clear_form()
        except Exception as ex:
            logger.error(f"Error saving artist: {ex}")
            self.show_error("Error", f"Failed to save artist: {str(ex)}")

    def edit_artist(self, artist_id: int):
        """Load artist data for editing."""
        logger.info(f"Editing artist {artist_id}")
        try:
            success, response = self.api_client.get_artist(artist_id)
            if success and response.get("success"):
                artist = response.get("artist", {})
                self.name_field.value = artist.get("name", "")
                self.specialties_field.value = artist.get("specialties", "")
                self.experience_field.value = str(artist.get("experience_years", ""))
                self.hourly_rate_field.value = str(artist.get("hourly_rate", ""))
                self.bio_field.value = artist.get("bio", "")
                self.active_checkbox.value = artist.get("active", True)
                self.editing_artist_id = artist_id
                self.page.update()
            else:
                error_msg = response.get("error", "Artist not found.")
                self.show_error("Error", error_msg)
        except Exception as ex:
            logger.error(f"Error loading artist for edit: {ex}")
            self.show_error("Error", f"Failed to load artist: {str(ex)}")

    def cancel_edit(self, e):
        """Cancel editing and clear form."""
        self.clear_form()
        self.editing_artist_id = None

    def clear_form(self):
        """Clear all form fields."""
        self.name_field.value = ""
        self.specialties_field.value = ""
        self.experience_field.value = ""
        self.hourly_rate_field.value = ""
        self.bio_field.value = ""
        self.active_checkbox.value = True
        self.page.update()

    def delete_artist_confirm(self, artist_id: int):
        """Show confirmation dialog for artist deletion."""

        def on_confirm(e):
            try:
                success, response = self.api_client.delete_artist(artist_id)
                if success and response.get("success"):
                    self.show_success("Artist deleted successfully.")
                    self.load_artists()
                else:
                    error_msg = response.get("error", "Failed to delete artist.")
                    self.show_error("Error", error_msg)
            except Exception as ex:
                logger.error(f"Error deleting artist: {ex}")
                self.show_error("Error", f"Failed to delete artist: {str(ex)}")
            self._close_dialog()

        confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm Delete"),
            content=ft.Text(
                "Are you sure you want to delete this artist?", color="#EF5350"
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self._close_dialog()),
                ft.TextButton("Delete", on_click=on_confirm),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.dialog = confirm_dialog
        if self.dialog not in self.page.overlay:
            self.page.overlay.append(self.dialog)
        self.dialog.open = True
        self.page.update()

    def search_artist(self, e):
        """Search artists by name."""
        query = (self.search_field.value or "").strip()
        if not query:
            self.load_artists()
            return
        logger.info(f"Searching artists by name: {query}")
        try:
            success, response = self.api_client.list_artists(search=query)
            if success and response.get("success"):
                self.current_artists = response.get("artists", [])
                self.update_artists_list()
            else:
                error_msg = response.get("error", "No artists found.")
                self.show_error("Error", error_msg)
        except Exception as ex:
            logger.error(f"Error searching artists: {ex}")
            self.show_error("Error", f"Failed to search artists: {str(ex)}")

    def refresh_artists(self, e):
        """Refresh the artists list."""
        self.load_artists()

    def show_error(self, title: str, message: str):
        """Show error dialog."""
        self._show_dialog(title, message, "#EF5350")  # RED_400 hex code

    def show_success(self, message: str):
        """Show success message."""
        self._show_dialog("Success", message, "#66BB6A")  # GREEN_400 hex code

    def show_info(self, title: str, message: str):
        """Show info dialog."""
        self._show_dialog(title, message, "#42A5F5")  # BLUE_400 hex code

    def _show_dialog(self, title: str, message: str, text_color: str):
        """Show a dialog with the given title, message and color."""
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(message, color=text_color),
            actions=[ft.TextButton("OK", on_click=lambda e: self._close_dialog())],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        if self.dialog not in self.page.overlay:
            self.page.overlay.append(self.dialog)
        self.dialog.open = True
        self.page.update()

    def _close_dialog(self):
        """Close the current dialog."""
        if hasattr(self, "dialog") and self.dialog is not None:
            self.dialog.open = False
            self.page.update()
