"""
Client Management Page for Tattoo Studio Management System.

This module provides the user interface for managing tattoo clients including:
- Displaying list of all clients
- Creating new clients
- Editing existing clients
- Deleting clients
- Searching clients by name

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


class ClientManagementPage:
    """
    Client management page component for the Flet application.

    Provides a complete interface for CRUD operations on clients,
    connected to the Flask backend API.
    """

    def __init__(self, page: ft.Page):
        """
        Initialize the client management page.

        Args:
            page (ft.Page): Flet page instance
        """
        self.page = page
        self.api_client = get_api_client()

        # UI components
        self.clients_list = ft.ListView()
        self.search_field = ft.TextField(
            label="Search by name", on_submit=self.search_client, suffix_icon="search"
        )
        self.name_field = ft.TextField(label="Name", hint_text="Enter client name")
        self.phone_field = ft.TextField(
            label="Phone (optional)", hint_text="e.g., +1234567890"
        )
        self.email_field = ft.TextField(
            label="Email (optional)", hint_text="client@example.com"
        )
        self.notes_field = ft.TextField(
            label="Notes (optional)",
            hint_text="Any additional information...",
            multiline=True,
            max_lines=3,
        )
        self.active_checkbox = ft.Checkbox(label="Active", value=True)

        # State
        self.current_clients: List[dict] = []
        self.editing_client_id: Optional[int] = None

        logger.info("Client management page initialized")

    def build(self) -> ft.View:
        """
        Build and return the client management page view.

        Returns:
            ft.View: Complete client management page
        """
        # Create form for adding/editing clients
        client_form = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Add/Edit Client", size=20, weight=ft.FontWeight.BOLD),
                        self.name_field,
                        self.phone_field,
                        self.email_field,
                        self.notes_field,
                        self.active_checkbox,
                        ft.Row(
                            [
                                ft.ElevatedButton(
                                    "Save Client",
                                    on_click=self.save_client,
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

        # Create client list section
        client_list_section = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text("Clients", size=20, weight=ft.FontWeight.BOLD),
                                ft.ElevatedButton(
                                    "Refresh",
                                    on_click=self.refresh_clients,
                                    icon="refresh",
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        self.search_field,
                        ft.Container(
                            content=self.clients_list,
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
                    content=client_form,
                    width=400,
                    expand=False,
                ),
                ft.Container(
                    content=client_list_section,
                    expand=True,
                ),
            ],
            spacing=20,
            expand=True,
        )

        return ft.View(
            route="/clients",
            controls=[
                ft.Container(
                    content=content,
                    padding=20,
                    expand=True,
                )
            ],
        )

    def load_clients(self):
        """Load clients from the API and update the UI."""
        logger.info("Loading clients from API")
        try:
            success, response = self.api_client.get_all_clients()
            if success and "clients" in response:
                self.current_clients = response["clients"]
                logger.info(f"Loaded {len(self.current_clients)} clients from API")
            else:
                self.current_clients = []
                error_msg = response.get("error", "Unknown error loading clients")
                logger.warning(f"API error: {error_msg}")
                self.show_error("Error", error_msg)
            self.update_clients_list()
        except Exception as e:
            logger.error(f"Error loading clients: {e}")
            self.show_error("Error", f"Failed to load clients: {str(e)}")

    def update_clients_list(self):
        """Update the clients list UI with current data."""
        self.clients_list.controls.clear()

        if not self.current_clients:
            self.clients_list.controls.append(
                ft.Container(
                    content=ft.Text(
                        "No clients found",
                        text_align=ft.TextAlign.CENTER,
                        color="#757575",  # GREY_600 hex code
                    ),
                    alignment=ft.alignment.center,
                    padding=20,
                )
            )
        else:
            for client in self.current_clients:
                self.clients_list.controls.append(self._create_client_tile(client))

        self.clients_list.update()

    def _create_client_tile(self, client: dict) -> ft.ListTile:
        """Create a list tile for a client."""
        status_color = (
            "#4CAF50" if client.get("active", True) else "#F44336"
        )  # GREEN/RED hex codes
        status_text = "Active" if client.get("active", True) else "Inactive"

        return ft.ListTile(
            leading=ft.Icon("person", color="#1E88E5"),  # BLUE_600 hex code
            title=ft.Text(client.get("name", "Unknown"), weight=ft.FontWeight.BOLD),
            subtitle=ft.Column(
                [
                    ft.Text(f"Phone: {client.get('phone', 'N/A')}"),
                    ft.Text(f"Email: {client.get('email', 'N/A')}"),
                    ft.Text(f"Status: {status_text}", color=status_color),
                ],
                spacing=2,
            ),
            trailing=ft.Row(
                [
                    ft.IconButton(
                        icon="edit",
                        tooltip="Edit client",
                        on_click=lambda e, cid=client["id"]: self.edit_client(cid),
                    ),
                    ft.IconButton(
                        icon="delete",
                        tooltip="Delete client",
                        icon_color="#EF5350",  # RED_400 hex code
                        on_click=lambda e, cid=client["id"]: self.delete_client_confirm(
                            cid
                        ),
                    ),
                ],
                tight=True,
            ),
        )

    def save_client(self, _e):
        """Save client data (create or update)."""
        name = (self.name_field.value or "").strip()
        phone = (self.phone_field.value or "").strip()
        email = (self.email_field.value or "").strip()
        notes = (self.notes_field.value or "").strip()
        active = self.active_checkbox.value if self.active_checkbox.value is not None else True

        if not name:
            self.show_error("Validation Error", "Client name is required.")
            return

        try:
            if self.editing_client_id is None:
                # Create new client
                success, response = self.api_client.create_client(
                    name=name, phone=phone, email=email, notes=notes, active=active
                )
                if success:
                    self.show_info("Success", "Client created successfully.")
                    self.clear_form()
                    self.load_clients()
                else:
                    self.show_error(
                        "Error", response.get("error", "Failed to create client.")
                    )
            else:
                # Update existing client
                success, response = self.api_client.update_client(
                    client_id=self.editing_client_id,
                    name=name,
                    phone=phone,
                    email=email,
                    notes=notes,
                    active=active,
                )
                if success:
                    self.show_info("Success", "Client updated successfully.")
                    self.clear_form()
                    self.editing_client_id = None
                    self.load_clients()
                else:
                    self.show_error(
                        "Error", response.get("error", "Failed to update client.")
                    )
        except Exception as e:
            logger.error(f"Error saving client: {e}")
            self.show_error("Error", f"Failed to save client: {str(e)}")

    def edit_client(self, client_id: int):
        """Load client data for editing."""
        try:
            success, response = self.api_client.get_client(client_id)
            if success and "client" in response:
                client = response["client"]
                self.name_field.value = client.get("name", "")
                self.phone_field.value = client.get("phone", "")
                self.email_field.value = client.get("email", "")
                self.notes_field.value = client.get("notes", "")
                self.active_checkbox.value = client.get("active", True)
                self.editing_client_id = client_id
                self.page.update()
            else:
                self.show_error(
                    "Error", response.get("error", "Failed to load client data.")
                )
        except Exception as e:
            logger.error(f"Error loading client for edit: {e}")
            self.show_error("Error", f"Failed to load client: {str(e)}")

    def cancel_edit(self, _e):
        """Cancel editing and clear form."""
        self.clear_form()
        self.editing_client_id = None

    def clear_form(self):
        """Clear all form fields."""
        self.name_field.value = ""
        self.phone_field.value = ""
        self.email_field.value = ""
        self.notes_field.value = ""
        self.active_checkbox.value = True
        self.page.update()

    def delete_client_confirm(self, client_id: int):
        """Show confirmation dialog and delete client if confirmed."""

        def on_confirm(_e):
            try:
                success, response = self.api_client.delete_client(client_id)
                if success:
                    self.show_info("Success", "Client deleted successfully.")
                    self.load_clients()
                else:
                    self.show_error(
                        "Error", response.get("error", "Failed to delete client.")
                    )
            except Exception as e:
                logger.error(f"Error deleting client: {e}")
                self.show_error("Error", f"Failed to delete client: {str(e)}")

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Delete Client"),
            content=ft.Text("Are you sure you want to delete this client?"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self._close_dialog()),
                ft.TextButton("Delete", on_click=on_confirm),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def search_client(self, _e):
        """Search clients by name."""
        query = (self.search_field.value or "").strip()
        if not query:
            self.show_error("Validation Error", "Please enter a name to search.")
            return
        try:
            success, response = self.api_client.search_client_by_name(query)
            if success and "client" in response:
                self.current_clients = [response["client"]]
                self.update_clients_list()
            else:
                error_msg = response.get("error", "No client found.")
                self.show_error("Search Result", error_msg)
                self.current_clients = []
                self.update_clients_list()
        except Exception as e:
            logger.error(f"Error searching client: {e}")
            self.show_error("Error", f"Failed to search client: {str(e)}")

    def refresh_clients(self, _e):
        """Refresh the clients list."""
        self.load_clients()

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

        def close_dialog(_):
            """Close the dialog."""
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(message, color=text_color),
            actions=[ft.TextButton("OK", on_click=close_dialog)],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # Correct way to show dialog in Flet using overlay
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def _close_dialog(self):
        """Close the current dialog."""
        # Remove any open dialogs from overlay
        for control in self.page.overlay[:]:
            if isinstance(control, ft.AlertDialog):
                control.open = False
                self.page.overlay.remove(control)
        self.page.update()
