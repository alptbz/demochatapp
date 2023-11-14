from threading import Thread
from typing import List

import flet as ft
from chatclient import ChatClient
from classes import ChatMessage


def main(page: ft.Page):
    page.horizontal_alignment = "stretch"
    page.title = "Flet Chat"

    chatclient = ChatClient("http://127.0.0.1:7080")

    def join_chat_click(e):
        if not join_user_name.value :
            join_user_name.error_text = "username  cannot be blank!"
            join_user_name.update()
        elif not join_pass_word.value:
            join_pass_word.error_text = "password cannot be blank!"
            join_pass_word.update()
        else:
            if not chatclient.login(join_user_name.value, join_pass_word.value):
                join_pass_word.error_text = "invalid login"
                join_pass_word.update()
            else:
                page.session.set("user_name", join_user_name.value)
                status_field.value = f"Logged in as {chatclient.username}"
                page.dialog.open = False
                new_message.prefix = ft.Text(f"{join_user_name.value}: ")
                page.update()

    def send_message_click(e):
        if new_message.value != "":
            chatclient.send_message(new_message.value)
            new_message.value = ""
            new_message.focus()
            page.update()

    # A dialog asking for a user display name
    join_user_name = ft.TextField(
        label="Enter your name to join the chat",
        autofocus=True,
        value="max"
    )
    join_pass_word = ft.TextField(
        label = "Password",
        autofocus=False,
        on_submit=join_chat_click,
        password=True,
        can_reveal_password=True,
        value="1234"
    )

    def on_alert_dialog_dismiss(e):
        if not chatclient.is_login():
            login_dialog.open = True
            page.dialog = login_dialog
            page.update()

    login_dialog = ft.AlertDialog(
        open=True,
        modal=True,
        title=ft.Text("Welcome!"),
        content=ft.Column([join_user_name, join_pass_word], width=300, height=150, tight=True),
        actions=[ft.ElevatedButton(text="Login", on_click=join_chat_click)],
        actions_alignment="end",
        on_dismiss=on_alert_dialog_dismiss

    )

    page.dialog = login_dialog

    # Chat messages
    chat = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
    )

    # A new message entry form
    new_message = ft.TextField(
        hint_text="Write a message...",
        autofocus=True,
        shift_enter=True,
        min_lines=1,
        max_lines=5,
        filled=True,
        expand=True,
        on_submit=send_message_click,
    )

    status_field = ft.Text(
        value="not logged in"
    )

    def on_select_conversation(e):
        chat.controls.clear()
        chatclient.select_conversation(e.data)
        messages = chatclient.get_active_conversation_chat_messages()
        for message in messages:
            chat.controls.append(message)
        page.update()

    users_dropdown = ft.Dropdown(
        options=[],
        label="Conversation:",
        on_change=on_select_conversation
    )

    def on_new_username(usernames: List[str]):
        usernames_not_added = usernames
        for o in users_dropdown.options:
            if o.key in usernames:
                usernames_not_added.remove(o.key)
            else:
                users_dropdown.options.remove(o)
        for u in usernames_not_added:
            users_dropdown.options.append(ft.dropdown.Option(u))
        users_dropdown.update()

    def on_new_message(chat_message: ChatMessage):
        chat.controls.append(chat_message)
        page.update()

    chatclient.on_new_userlist = on_new_username
    chatclient.on_new_message = on_new_message

    # Add everything to the page
    page.add(
        status_field,
        users_dropdown,
        ft.Container(
            content=chat,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=5,
            padding=10,
            expand=True,
        ),
        ft.Row(
            [
                new_message,
                ft.IconButton(
                    icon=ft.icons.SEND_ROUNDED,
                    tooltip="Send message",
                    on_click=send_message_click,
                ),
            ]
        ),
    )

#ft.app(target=main, port=8835, view=ft.WEB_BROWSER)
ft.app(target=main)
