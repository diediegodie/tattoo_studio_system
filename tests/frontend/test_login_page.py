"""
Test for Login Page UI (Flet)
- Normal case: fields and buttons present
- Edge case: empty fields
- Failure case: invalid email format (UI only)

Run with: pytest
"""

import flet as ft
import pytest
from frontend.pages.login import login_page

# Helper: Dummy handlers
login_called = {}

def dummy_login(email, password):
    login_called["email"] = email
    login_called["password"] = password
    login_called["called"] = True

def dummy_register(email, password):
    login_called["register"] = True

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

def test_login_page_renders_fields_and_buttons():
    """Normal case: Login page renders all fields and buttons."""
    view = login_page(dummy_login, dummy_register)
    textfields = find_controls_of_type(view, ft.TextField)
    assert len(textfields) == 2
    assert any("Email" in tf.label for tf in textfields)
    assert any("Password" in tf.label for tf in textfields)
    rows = find_controls_of_type(view, ft.Row)
    assert rows, "No Row found in login page"
    buttons = rows[0].controls
    assert any(isinstance(b, ft.ElevatedButton) and b.text == "Login" for b in buttons)
    assert any(isinstance(b, ft.OutlinedButton) and b.text == "Register" for b in buttons)

def test_login_page_empty_fields():
    """Edge case: Submitting with empty fields calls handler with empty strings."""
    login_called.clear()
    view = login_page(dummy_login, dummy_register)
    rows = find_controls_of_type(view, ft.Row)
    assert rows, "No Row found for buttons"
    login_btn = rows[0].controls[0]
    login_btn.on_click(None)  # Should call dummy_login with empty strings
    assert login_called.get("called")
    assert login_called.get("email", None) == ""
    assert login_called.get("password", None) == ""

def test_login_page_invalid_email_ui():
    """Failure case: UI does not validate email, but field is present."""
    view = login_page(dummy_login, dummy_register)
    textfields = find_controls_of_type(view, ft.TextField)
    email_field = [tf for tf in textfields if isinstance(tf.label, str) and "Email" in tf.label][0]
    # Simulate entering invalid email
    email_field.value = "not-an-email"
    assert email_field.value == "not-an-email"
    # No validation at UI level (handled by backend or later)