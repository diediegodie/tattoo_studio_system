"""
Admin Tools Page for Backup and Migration
"""

import flet as ft
from frontend.utils.api_client import APIClient


class AdminToolsPage(ft.Control):
    def __init__(self, user_role):
        super().__init__()
        self.user_role = user_role
        self.api = APIClient()
        self.backup_status = ft.Text("Last backup: --")
        self.backup_msg = ft.Text("")
        self.migration_status = ft.Text("Current migration version: --")
        self.migration_msg = ft.Text("")
        self.backup_btn = ft.ElevatedButton("Run Backup", on_click=self.run_backup)
        self.migration_btn = ft.ElevatedButton(
            "Run Migration", on_click=self.run_migration
        )
        self.progress = ft.ProgressRing(visible=False)

    def get_content(self):
        if self.user_role != "admin":
            return ft.Column([ft.Text("Access denied: Admins only.", color="red")])
        else:
            return ft.Column(
                [
                    ft.Text("Admin Tools", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                    ft.Divider(),
                    ft.Text("Database Backup", style=ft.TextThemeStyle.TITLE_MEDIUM),
                    self.backup_btn,
                    self.backup_status,
                    self.backup_msg,
                    ft.Divider(),
                    ft.Text("Database Migration", style=ft.TextThemeStyle.TITLE_MEDIUM),
                    self.migration_btn,
                    self.migration_status,
                    self.migration_msg,
                    self.progress,
                ]
            )

    def build(self):
        self.content = self.get_content()

    def run_backup(self, e):
        self.progress.visible = True
        self.backup_btn.disabled = True
        self.update()
        try:
            resp = self.api.post("/api/backup/database")
            if resp and resp.get("status") == "SUCCESS":
                from datetime import datetime

                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.backup_status.value = f"Last backup: {now}"
                self.backup_msg.value = "Backup completed successfully."
            else:
                self.backup_msg.value = (
                    f"Backup failed: {resp.get('error', 'Unknown error')}"
                )
        except Exception as ex:
            self.backup_msg.value = f"Backup error: {ex}"
        self.progress.visible = False
        self.backup_btn.disabled = False
        self.update()

    def run_migration(self, e):
        self.progress.visible = True
        self.migration_btn.disabled = True
        self.update()
        try:
            resp = self.api.post("/api/migration/upgrade")
            if resp and resp.get("status") == "SUCCESS":
                version = resp.get("version", "unknown")
                self.migration_status.value = f"Current migration version: {version}"
                self.migration_msg.value = "Migration completed successfully."
            else:
                self.migration_msg.value = (
                    f"Migration failed: {resp.get('error', 'Unknown error')}"
                )
        except Exception as ex:
            self.migration_msg.value = f"Migration error: {ex}"
        self.progress.visible = False
        self.migration_btn.disabled = False
        self.update()
