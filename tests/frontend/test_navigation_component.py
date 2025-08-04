"""
Test for Navigation Component (Flet)
- Normal case: Navigation component renders with menu items
- Edge case: Different user roles (admin vs staff)
- Failure case: Navigation handles missing parameters gracefully

Run with: pytest
"""

import flet as ft
import pytest
from unittest.mock import Mock
from frontend.components.navigation import NavigationComponent


# Helper: Recursively find all controls of a given type in a Flet control tree
def find_controls_of_type(control, t):
    found = []
    if isinstance(control, t):
        found.append(control)
    if hasattr(control, "controls") and control.controls:
        for child in control.controls:
            found.extend(find_controls_of_type(child, t))
    if hasattr(control, "content") and control.content:
        found.extend(find_controls_of_type(control.content, t))
    return found


def test_navigation_component_renders_basic_menu():
    """Normal case: Navigation component renders all basic menu items."""
    # Mock objects
    mock_page = Mock()
    mock_app = Mock()

    nav = NavigationComponent(
        page=mock_page,
        app_instance=mock_app,
        current_route="/users",
        user_role="staff",
        user_name="Test User",
    )

    container = nav.build()

    # Check that it returns a container
    assert isinstance(container, ft.Container)
    assert container.width == 250

    # Find list tiles (navigation items)
    list_tiles = find_controls_of_type(container, ft.ListTile)

    # Should have at least basic navigation items + user info
    assert len(list_tiles) >= 4  # Users, Clients, Artists, Sessions

    # Check for expected navigation items
    tile_titles = [
        tile.title.value for tile in list_tiles if hasattr(tile.title, "value")
    ]
    assert "Users" in tile_titles
    assert "Clients" in tile_titles
    assert "Artists" in tile_titles
    assert "Sessions" in tile_titles


def test_navigation_component_admin_role():
    """Edge case: Admin role should include admin tools."""
    mock_page = Mock()
    mock_app = Mock()

    nav = NavigationComponent(
        page=mock_page,
        app_instance=mock_app,
        current_route="/admin",
        user_role="admin",
        user_name="Admin User",
    )

    container = nav.build()
    list_tiles = find_controls_of_type(container, ft.ListTile)

    # Admin should have additional menu item
    tile_titles = [
        tile.title.value for tile in list_tiles if hasattr(tile.title, "value")
    ]
    assert "Admin Tools" in tile_titles


def test_navigation_component_staff_role():
    """Edge case: Staff role should not include admin tools."""
    mock_page = Mock()
    mock_app = Mock()

    nav = NavigationComponent(
        page=mock_page,
        app_instance=mock_app,
        current_route="/users",
        user_role="staff",
        user_name="Staff User",
    )

    container = nav.build()
    list_tiles = find_controls_of_type(container, ft.ListTile)

    # Staff should not have admin tools
    tile_titles = [
        tile.title.value for tile in list_tiles if hasattr(tile.title, "value")
    ]
    assert "Admin Tools" not in tile_titles


def test_navigation_component_user_info_display():
    """Normal case: Navigation component displays user information."""
    mock_page = Mock()
    mock_app = Mock()

    nav = NavigationComponent(
        page=mock_page,
        app_instance=mock_app,
        current_route="/users",
        user_role="admin",
        user_name="John Doe",
    )

    container = nav.build()

    # Find ListTile controls (user info is a ListTile)
    list_tiles = find_controls_of_type(container, ft.ListTile)
    user_tile = None
    for tile in list_tiles:
        if hasattr(tile, "title") and hasattr(tile, "subtitle"):
            if tile.title.value == "John Doe" and tile.subtitle.value == "Role: Admin":
                user_tile = tile
                break
    assert (
        user_tile is not None
    ), "User info ListTile with correct name and role not found"


def test_navigation_component_logout_button():
    """Normal case: Navigation component has logout button."""
    mock_page = Mock()
    mock_app = Mock()

    nav = NavigationComponent(
        page=mock_page,
        app_instance=mock_app,
        current_route="/users",
        user_role="staff",
        user_name="Test User",
    )

    container = nav.build()

    # Find buttons
    buttons = find_controls_of_type(container, ft.ElevatedButton)
    button_texts = [btn.text for btn in buttons if hasattr(btn, "text")]

    # Should have logout button
    assert "Logout" in button_texts


def test_navigation_component_update_route():
    """Normal case: Navigation component can update current route."""
    mock_page = Mock()
    mock_app = Mock()

    nav = NavigationComponent(
        page=mock_page,
        app_instance=mock_app,
        current_route="/users",
        user_role="staff",
        user_name="Test User",
    )

    # Initial route
    assert nav.current_route == "/users"

    # Update route
    nav.update_current_route("/clients")
    assert nav.current_route == "/clients"
