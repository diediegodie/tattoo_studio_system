"""
Main Flet Frontend Application for Tattoo Studio Management System.

This is the entry point for the desktop application built with Flet.
It provides a complete user interface that communicates with the Flask
backend API for all data operations.

Features:
- User management with full CRUD operations
- Real-time data synchronization with backend
- Error handling and user-friendly messages
- Responsive UI design

Usage:
    python frontend/main.py
"""

import flet as ft
import sys
import os
from typing import Optional

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from frontend.pages.users import UserManagementPage
from frontend.pages.login import login_page
from frontend.utils.api_client import get_api_client
from utils.logger import setup_logger

# Initialize logger
logger = setup_logger(__name__)


class TattooStudioApp:
    """
    Main application class for the Tattoo Studio Management System.
    Manages navigation between different pages and handles the overall
    application state and lifecycle.
    """

    def __init__(self):
        """Initialize the application."""
        self.api_client = get_api_client()
        self.user_page: Optional[UserManagementPage] = None
        logger.info("Tattoo Studio App initialized")

        # JWT token (in-memory)
        self.jwt_token = None
        self.is_authenticated = False

    def store_token(self, page, token: str):
        """Store JWT token in memory and client storage."""
        self.jwt_token = token
        self.api_client.set_token(token)
        page.client_storage.set("jwt_token", token)

    def load_token(self, page):
        """Load JWT token from client storage if available."""
        token = page.client_storage.get("jwt_token")
        if token:
            self.jwt_token = token
            self.api_client.set_token(token)
            self.is_authenticated = True
        else:
            self.jwt_token = None
            self.api_client.clear_token()
            self.is_authenticated = False

    def clear_token(self, page):
        """Clear JWT token from memory and client storage."""
        self.jwt_token = None
        self.api_client.clear_token()
        page.client_storage.remove("jwt_token")
        self.is_authenticated = False

    def main(self, page: ft.Page):
        """
        Main application entry point called by Flet.
        Args:
            page (ft.Page): The main Flet page instance
        """
        # Configure page
        page.title = "Tattoo Studio Management System"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.window.width = 1200
        page.window.height = 800
        page.window.min_width = 800
        page.window.min_height = 600

        # Initialize pages
        self.user_page = UserManagementPage(page)

        def handle_login(email, password):
            """
            Handle login: call API, store JWT, set auth state, redirect.
            """
            logger.info(f"Login attempt: {email}")
            success, resp = self.api_client.login(email=email, password=password)
            if success and "access_token" in resp:
                token = resp["access_token"]
                self.store_token(page, token)
                logger.info("Login successful, JWT stored.")
                snack = ft.SnackBar(ft.Text("Login successful!"), open=True)
                page.overlay.append(snack)
                page.update()
                page.go("/users")
            else:
                self.clear_token(page)
                error_msg = resp.get("error", "Login failed. Check credentials.")
                logger.warning(f"Login failed: {error_msg}")
                snack = ft.SnackBar(ft.Text(f"Login failed: {error_msg}"), open=True)
                page.overlay.append(snack)
                page.update()
                page.go("/login")

        def handle_register(email, password):
            """
            Handle register: call API, show result.
            """
            logger.info(f"Register attempt: {email}")
            # Call backend /auth/register
            success, resp = self.api_client._make_request(
                "POST", "/auth/register", json={"email": email, "password": password}
            )
            if success:
                snack = ft.SnackBar(
                    ft.Text("Registration successful! Please log in."), open=True
                )
                page.overlay.append(snack)
                page.update()
                page.go("/login")
            else:
                error_msg = resp.get("error", "Registration failed.")
                logger.warning(f"Register failed: {error_msg}")
                snack = ft.SnackBar(ft.Text(f"Register failed: {error_msg}"), open=True)
                page.overlay.append(snack)
                page.update()
                page.go("/login")

        def route_change(route):
            """Handle route changes and authentication state."""
            # Load token from client storage on every route change
            self.load_token(page)
            # If not authenticated, redirect to login
            if not self.jwt_token:
                logger.info("No JWT token found, redirecting to login.")
                page.go("/login")
                return
            # If token is present but API returns 401, clear and redirect
            # This is handled in APIClient._make_request, but double check here
            if not self.is_authenticated:
                logger.info("JWT token invalid/expired, redirecting to login.")
                page.go("/login")
                return
            # ...existing code...
            logger.info(f"Route changed to: {route.route}")

            # Check token presence (simple check)
            if not self.jwt_token:
                self.is_authenticated = False
                self.api_client.clear_token()

            page.views.clear()

            if not self.is_authenticated:
                # Always show login page if not authenticated
                page.views.append(login_page(handle_login, handle_register))
                page.update()
                return

            # Authenticated: show requested page
            if page.route == "/users" or page.route == "/":
                if self.user_page:
                    page.views.append(self.user_page.build())
                    self.user_page.load_users()
            else:
                # Default route - redirect to users
                if self.user_page:
                    page.views.append(self.user_page.build())
                    self.user_page.load_users()

            page.update()

        def view_pop(view):
            """Handle view pop events."""
            page.views.pop()
            if page.views:
                top_view = page.views[-1]
                if hasattr(top_view, "route") and top_view.route:
                    page.go(top_view.route)
                else:
                    page.go("/users")
            else:
                # If no views left, force login
                self.is_authenticated = False
                self.jwt_token = None
                self.api_client.clear_token()
                page.go("/login")

        # Set up routing
        page.on_route_change = route_change
        page.on_view_pop = view_pop

        # Check backend connection on startup
        self.check_backend_connection(page)

        # Navigate to default route
        page.go("/users")

    def check_backend_connection(self, page: ft.Page):
        """
        Check if the backend API is accessible and show status.

        Args:
            page (ft.Page): Flet page instance for showing dialogs
        """
        try:
            success, response = self.api_client.health_check()

            if success:
                logger.info("Backend connection successful")
                self.show_connection_status(page, True, "Connected to backend API")
            else:
                error_msg = response.get("error", "Unknown error")
                logger.warning(f"Backend connection failed: {error_msg}")
                self.show_connection_status(
                    page, False, f"Backend connection failed: {error_msg}"
                )

        except Exception as e:
            logger.error(f"Error checking backend connection: {e}")
            self.show_connection_status(page, False, f"Connection error: {str(e)}")

    def show_connection_status(self, page: ft.Page, success: bool, message: str):
        """
        Show connection status to user.

        Args:
            page (ft.Page): Flet page instance
            success (bool): Whether connection was successful
            message (str): Status message to display
        """
        color = "#4CAF50" if success else "#F44336"  # Green or Red
        icon_name = "check_circle" if success else "error"

        # Show a brief snack bar notification
        snack_bar = ft.SnackBar(
            content=ft.Row(
                [ft.Icon(icon_name, color=color), ft.Text(message, color=color)]
            ),
            duration=3000 if success else 5000,  # Show errors longer
        )

        page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()


def main():
    """
    Application entry point.

    Starts the Flet desktop application.
    """
    try:
        logger.info("Starting Tattoo Studio Management System")

        app = TattooStudioApp()

        # Start the Flet app
        ft.app(
            target=app.main,
            name="Tattoo Studio Management",
            view=ft.AppView.FLET_APP,  # Desktop app mode
        )

    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
