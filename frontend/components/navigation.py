"""
Navigation Component for Tattoo Studio Management System.

This module provides the main navigation sidebar/tabs for the Flet application.
It handles routing between different pages and shows the current user context.

Features:
- Sidebar navigation with icons
- User information display
- Logout functionality
- Active page highlighting
- Role-based menu visibility

Usage:
    nav = NavigationComponent(page, app_instance, current_route)
    content = nav.build()
"""

import flet as ft
from typing import Callable, Optional
import sys
import os

# Add project root to path for imports
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)

from utils.logger import setup_logger

# Initialize logger
logger = setup_logger(__name__)


class NavigationComponent:
    """
    Main navigation component for the application.

    Provides a sidebar with navigation items, user info, and logout functionality.
    """

    def __init__(
        self,
        page: ft.Page,
        app_instance,
        current_route: str = "/users",
        user_role: str = "staff",
        user_name: str = "User",
    ):
        """
        Initialize the navigation component.

        Args:
            page (ft.Page): Flet page instance
            app_instance: Main app instance for logout handling
            current_route (str): Currently active route
            user_role (str): Current user role (admin/staff)
            user_name (str): Current user name
        """
        self.page = page
        self.app = app_instance
        self.current_route = current_route
        self.user_role = user_role
        self.user_name = user_name

        logger.info(f"Navigation component initialized for user: {user_name}")

    def build(self) -> ft.Container:
        """
        Build and return the navigation sidebar.

        Returns:
            ft.Container: Complete navigation sidebar
        """
        # Navigation menu items
        nav_items = [
            {
                "title": "Users",
                "icon": "people",
                "route": "/users",
                "description": "Manage system users",
            },
            {
                "title": "Clients",
                "icon": "person",
                "route": "/clients",
                "description": "Manage tattoo clients",
            },
            {
                "title": "Artists",
                "icon": "brush",
                "route": "/artists",
                "description": "Manage tattoo artists",
            },
            {
                "title": "Sessions",
                "icon": "event",
                "route": "/sessions",
                "description": "Manage tattoo sessions",
            },
        ]

        # Add admin-only items
        if self.user_role == "admin":
            nav_items.append(
                {
                    "title": "Admin Tools",
                    "icon": "admin_panel_settings",
                    "route": "/admin",
                    "description": "Database backup & migration",
                }
            )

        # Create navigation items
        nav_controls = []
        for item in nav_items:
            is_active = self.current_route == item["route"]
            nav_controls.append(self._create_nav_item(item, is_active))

        # User info section
        user_info = ft.Container(
            content=ft.Column(
                [
                    ft.Divider(),
                    ft.ListTile(
                        leading=ft.Icon("account_circle", size=40),
                        title=ft.Text(
                            self.user_name,
                            weight=ft.FontWeight.BOLD,
                            size=16,
                        ),
                        subtitle=ft.Text(
                            f"Role: {self.user_role.title()}",
                            size=12,
                            color="#757575",  # GREY_600 hex code
                        ),
                    ),
                    ft.ElevatedButton(
                        "Logout",
                        icon="logout",
                        width=200,
                        on_click=self._handle_logout,
                        style=ft.ButtonStyle(
                            color="#FFFFFF",  # WHITE hex code
                            bgcolor="#EF5350",  # RED_400 hex code
                        ),
                    ),
                ]
            ),
            padding=ft.padding.all(10),
        )

        # Main sidebar container
        sidebar = ft.Container(
            content=ft.Column(
                [
                    # Header
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon("palette", size=40, color=ft.Colors.BLUE_600),
                                ft.Text(
                                    "Tattoo Studio",
                                    size=20,
                                    weight=ft.FontWeight.BOLD,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                ft.Text(
                                    "Management System",
                                    size=12,
                                    color=ft.Colors.GREY_600,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=ft.padding.all(20),
                        margin=ft.margin.only(bottom=10),
                    ),
                    ft.Divider(),
                    # Navigation items
                    ft.Container(
                        content=ft.Column(nav_controls, spacing=5),
                        expand=True,
                        padding=ft.padding.all(10),
                    ),
                    # User info at bottom
                    user_info,
                ]
            ),
            width=250,
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.border_radius.only(top_right=10, bottom_right=10),
            padding=ft.padding.all(0),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
                offset=ft.Offset(2, 0),
            ),
        )

        return sidebar

    def _create_nav_item(self, item: dict, is_active: bool) -> ft.Container:
        """
        Create a navigation item.

        Args:
            item (dict): Navigation item data
            is_active (bool): Whether this item is currently active

        Returns:
            ft.Container: Navigation item container
        """
        # Colors based on active state
        if is_active:
            bg_color = ft.Colors.BLUE_100
            text_color = ft.Colors.BLUE_800
            icon_color = ft.Colors.BLUE_600
        else:
            bg_color = ft.Colors.TRANSPARENT
            text_color = ft.Colors.ON_SURFACE
            icon_color = ft.Colors.ON_SURFACE_VARIANT

        nav_item = ft.Container(
            content=ft.ListTile(
                leading=ft.Icon(
                    item["icon"],
                    color=icon_color,
                    size=24,
                ),
                title=ft.Text(
                    item["title"],
                    color=text_color,
                    weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL,
                ),
                subtitle=ft.Text(
                    item["description"],
                    size=11,
                    color=ft.Colors.GREY_600,
                ),
                on_click=lambda e, route=item["route"]: self._navigate_to(route),
            ),
            bgcolor=bg_color,
            border_radius=ft.border_radius.all(8),
            padding=ft.padding.symmetric(horizontal=5, vertical=2),
        )

        return nav_item

    def _navigate_to(self, route: str):
        """
        Handle navigation to a specific route.

        Args:
            route (str): Target route to navigate to
        """
        logger.info(f"Navigating to: {route}")
        self.page.go(route)

    def _handle_logout(self, e):
        """Handle logout button click."""
        logger.info("User logout requested")

        # Show confirmation dialog
        def confirm_logout(e):
            self.app.clear_token(self.page)
            self.page.go("/login")
            dialog.open = False
            self.page.update()

        def cancel_logout(e):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm Logout"),
            content=ft.Text("Are you sure you want to logout?"),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_logout),
                ft.ElevatedButton(
                    "Logout",
                    on_click=confirm_logout,
                    style=ft.ButtonStyle(bgcolor=ft.Colors.RED_400),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def update_current_route(self, route: str):
        """
        Update the current active route.

        Args:
            route (str): New current route
        """
        self.current_route = route
        logger.debug(f"Navigation route updated to: {route}")
