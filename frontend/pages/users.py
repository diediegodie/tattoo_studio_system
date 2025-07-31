"""
User Management Page for Tattoo Studio Management System.

This module provides the user interface for managing users including:
- Displaying list of all users
- Creating new users
- Editing existing users
- Deleting users
- Searching users by name

Uses the API client to communicate with the Flask backend.
"""

import flet as ft
from typing import List, Optional
import sys
import os

# Add project root to path for imports
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)

from frontend.utils.api_client import get_api_client
from utils.logger import setup_logger

# Initialize logger
logger = setup_logger(__name__)


class UserManagementPage:
    """
    User management page component for the Flet application.

    Provides a complete interface for CRUD operations on users,
    connected to the Flask backend API.
    """

    def __init__(self, page: ft.Page):
        """
        Initialize the user management page.

        Args:
            page (ft.Page): Flet page instance
        """
        self.page = page
        self.api_client = get_api_client()

        # UI components
        self.users_list = ft.ListView()
        self.search_field = ft.TextField(
            label="Search by name", on_submit=self.search_user, suffix_icon="search"
        )
        self.name_field = ft.TextField(label="Name", hint_text="Enter user name")
        self.birth_field = ft.TextField(
            label="Birth Year (optional)",
            hint_text="e.g., 1990",
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self.active_checkbox = ft.Checkbox(label="Active", value=True)

        # State
        self.current_users: List[dict] = []
        self.editing_user_id: Optional[int] = None

        logger.info("User management page initialized")

    def build(self) -> ft.View:
        """
        Build and return the user management page view.

        Returns:
            ft.View: Complete user management page
        """
        # Create form for adding/editing users
        user_form = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Add/Edit User", size=20, weight=ft.FontWeight.BOLD),
                        self.name_field,
                        self.birth_field,
                        self.active_checkbox,
                        ft.Row(
                            [
                                ft.ElevatedButton(
                                    "Save User", on_click=self.save_user, icon="save"
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

        # Create user list section
        user_list_section = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text("Users", size=20, weight=ft.FontWeight.BOLD),
                                ft.ElevatedButton(
                                    "Refresh",
                                    on_click=self.refresh_users,
                                    icon="refresh",
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        self.search_field,
                        ft.Container(
                            content=self.users_list,
                            height=400,
                            border=ft.border.all(1, "#E0E0E0"),
                        ),
                    ]
                ),
                padding=20,
            )
        )

        # Main layout
        return ft.View(
            "/users",
            [
                ft.AppBar(title=ft.Text("User Management"), bgcolor="#F5F5F5"),
                ft.Row(
                    [
                        ft.Container(user_form, width=400),
                        ft.Container(user_list_section, expand=True),
                    ],
                    expand=True,
                ),
            ],
        )

    def load_users(self):
        """Load users from the backend API and update the UI."""
        try:
            success, response = self.api_client.get_all_users(active_only=False)

            if success:
                self.current_users = response.get("users", [])
                self.update_users_list()
                logger.info(f"Loaded {len(self.current_users)} users")
            else:
                self.show_error(
                    "Failed to load users", response.get("error", "Unknown error")
                )

        except Exception as e:
            logger.error(f"Error loading users: {e}")
            self.show_error("Error", f"Failed to load users: {str(e)}")

    def update_users_list(self):
        """Update the users list view with current data."""
        self.users_list.controls.clear()

        if not self.current_users:
            self.users_list.controls.append(
                ft.ListTile(
                    title=ft.Text("No users found"),
                    subtitle=ft.Text("Add a new user to get started"),
                )
            )
        else:
            for user in self.current_users:
                # Create user list item
                status_color = (
                    "#4CAF50" if user["active"] else "#F44336"
                )  # Green or Red
                status_text = "Active" if user["active"] else "Inactive"
                birth_text = (
                    f"Born: {user['birth']}" if user["birth"] else "Birth year not set"
                )

                list_item = ft.ListTile(
                    leading=ft.Icon("person", color=status_color),
                    title=ft.Text(user["name"], weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(
                        f"ID: {user['id']} | {birth_text} | Status: {status_text}"
                    ),
                    trailing=ft.Row(
                        [
                            ft.IconButton(
                                icon="edit",
                                tooltip="Edit user",
                                on_click=lambda e, user_id=user["id"]: self.edit_user(
                                    user_id
                                ),
                            ),
                            ft.IconButton(
                                icon="delete",
                                tooltip="Delete user",
                                icon_color="#F44336",
                                on_click=lambda e, user_id=user[
                                    "id"
                                ]: self.delete_user_confirm(user_id),
                            ),
                        ],
                        tight=True,
                    ),
                )

                self.users_list.controls.append(list_item)

        self.page.update()

    def save_user(self, e):
        """Save user (create new or update existing)."""
        try:
            # Validate input
            name = self.name_field.value.strip() if self.name_field.value else ""
            if not name:
                self.show_error("Validation Error", "Name is required")
                return

            birth = None
            if self.birth_field.value:
                try:
                    birth = int(self.birth_field.value)
                except ValueError:
                    self.show_error(
                        "Validation Error", "Birth year must be a valid number"
                    )
                    return

            active = self.active_checkbox.value or False

            # Call appropriate API method
            if self.editing_user_id:
                success, response = self.api_client.update_user(
                    self.editing_user_id, name=name, birth=birth, active=active
                )
                action = "updated"
            else:
                success, response = self.api_client.create_user(
                    name=name, birth=birth, active=active
                )
                action = "created"

            if success:
                self.show_success(f"User {action} successfully!")
                self.clear_form()
                self.load_users()  # Refresh the list
            else:
                error_msg = response.get("error", "Unknown error")
                self.show_error(f"Failed to {action.rstrip('d')} user", error_msg)

        except Exception as e:
            logger.error(f"Error saving user: {e}")
            self.show_error("Error", f"Failed to save user: {str(e)}")

    def edit_user(self, user_id: int):
        """Load user data into form for editing."""
        try:
            success, response = self.api_client.get_user(user_id)

            if success:
                user = response["user"]
                self.editing_user_id = user_id

                # Populate form fields
                self.name_field.value = user["name"]
                self.birth_field.value = str(user["birth"]) if user["birth"] else ""
                self.active_checkbox.value = user["active"]

                self.page.update()
                logger.info(f"Editing user: {user['name']}")
            else:
                self.show_error("Error", response.get("error", "Failed to load user"))

        except Exception as e:
            logger.error(f"Error loading user for edit: {e}")
            self.show_error("Error", f"Failed to load user: {str(e)}")

    def cancel_edit(self, e):
        """Cancel editing and clear the form."""
        self.clear_form()

    def clear_form(self):
        """Clear the user form."""
        self.editing_user_id = None
        self.name_field.value = ""
        self.birth_field.value = ""
        self.active_checkbox.value = True
        self.page.update()

    def delete_user_confirm(self, user_id: int):
        """Show confirmation dialog for user deletion."""

        def delete_confirmed(e):
            self.delete_user(user_id)
            dialog.open = False
            self.page.update()

        def delete_cancelled(e):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Confirm Deletion"),
            content=ft.Text(
                "Are you sure you want to delete this user? This action cannot be undone."
            ),
            actions=[
                ft.TextButton("Cancel", on_click=delete_cancelled),
                ft.TextButton(
                    "Delete",
                    on_click=delete_confirmed,
                    style=ft.ButtonStyle(color="#F44336"),
                ),
            ],
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def delete_user(self, user_id: int):
        """Delete a user."""
        try:
            success, response = self.api_client.delete_user(user_id)

            if success:
                self.show_success("User deleted successfully!")
                self.load_users()  # Refresh the list

                # Clear form if we were editing this user
                if self.editing_user_id == user_id:
                    self.clear_form()
            else:
                error_msg = response.get("error", "Unknown error")
                self.show_error("Failed to delete user", error_msg)

        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            self.show_error("Error", f"Failed to delete user: {str(e)}")

    def search_user(self, e):
        """Search for a user by name."""
        try:
            name = (self.search_field.value or "").strip()
            if not name:
                self.load_users()  # Show all users if search is empty
                return

            success, response = self.api_client.search_user_by_name(name)

            if success:
                user = response["user"]
                self.current_users = [user]  # Show only the found user
                self.update_users_list()
                logger.info(f"Found user: {user['name']}")
            else:
                self.current_users = []
                self.update_users_list()
                self.show_info("No Results", f"No user found with name '{name}'")

        except Exception as e:
            logger.error(f"Error searching user: {e}")
            self.show_error("Error", f"Search failed: {str(e)}")

    def refresh_users(self, e):
        """Refresh the users list."""
        self.search_field.value = ""  # Clear search
        self.load_users()
        self.page.update()

    def show_error(self, title: str, message: str):
        """Show error dialog."""
        self._show_dialog(title, message, "#F44336")  # Red

    def show_success(self, message: str):
        """Show success dialog."""
        self._show_dialog("Success", message, "#4CAF50")  # Green

    def show_info(self, title: str, message: str):
        """Show info dialog."""
        self._show_dialog(title, message, "#2196F3")  # Blue

    def _show_dialog(self, title: str, message: str, text_color: str):
        """Show a dialog with the given title, message, and color."""

        def close_dialog(e):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text(title, color=text_color),
            content=ft.Text(message),
            actions=[ft.TextButton("OK", on_click=close_dialog)],
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
