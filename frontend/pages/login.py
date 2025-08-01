"""
Login Page for Tattoo Studio Management App (Flet)
- Email and password fields
- Login and Register buttons
- Modular, ready for integration

Follows project coding guidelines.
"""

import flet as ft


def login_page(on_login, on_register):
    """Login page UI with email and password fields, Login and Register buttons.

    Args:
        on_login (callable): Function to call on login button press.
        on_register (callable): Function to call on register button press.
    Returns:
        ft.View: Flet View with login form.
    """
    email_field = ft.TextField(label="Email", width=300, autofocus=True)
    password_field = ft.TextField(label="Password", password=True, width=300)
    login_btn = ft.ElevatedButton(
        "Login",
        width=140,
        on_click=lambda e: on_login(email_field.value, password_field.value),
    )
    register_btn = ft.OutlinedButton(
        "Register",
        width=140,
        on_click=lambda e: on_register(email_field.value, password_field.value),
    )

    form = ft.Column(
        [
            ft.Text("Tattoo Studio Login", size=24, weight=ft.FontWeight.BOLD),
            email_field,
            password_field,
            ft.Row([login_btn, register_btn], alignment=ft.MainAxisAlignment.CENTER),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20,
    )

    return ft.View(
        route="/login",
        controls=[
            ft.Container(
                content=form,
                alignment=ft.alignment.center,
                padding=40,
                expand=True,
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
    )
