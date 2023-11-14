from typing import List
import flet as ft


class Message():
    def __init__(self, sender: str, receiver: str, message: str, created: str):
        self.message = message
        self.receiver = receiver
        self.sender = sender
        self.message_type = "chat_message"
        self.created = created


class ChatMessage(ft.Row):
    def __init__(self, message: Message):
        super().__init__()
        self.vertical_alignment="start"
        self.controls=[
                ft.CircleAvatar(
                    content=ft.Text(self.get_initials(message.sender)),
                    color=ft.colors.WHITE,
                    bgcolor=self.get_avatar_color(message.sender),
                ),
                ft.Column(
                    [
                        ft.Text(message.sender, weight="bold"),
                        ft.Text(message.message, selectable=True),
                    ],
                    tight=True,
                    spacing=5,
                ),
            ]
    def get_initials(self, user_name: str):
        if user_name:
            return user_name[:1].capitalize()
        else:
            return "Unknown"  # or any default value you prefer

    def get_avatar_color(self, user_name: str):
        colors_lookup = [
            ft.colors.AMBER,
            ft.colors.BLUE,
            ft.colors.BROWN,
            ft.colors.CYAN,
            ft.colors.GREEN,
            ft.colors.INDIGO,
            ft.colors.LIME,
            ft.colors.ORANGE,
            ft.colors.PINK,
            ft.colors.PURPLE,
            ft.colors.RED,
            ft.colors.TEAL,
            ft.colors.YELLOW,
        ]
        return colors_lookup[hash(user_name) % len(colors_lookup)]


class ChatConversation:

    def __init__(self, username: str):
        self.username = username
        self.messages: List[Message] = []
        self.last_pos = 0
        self.on_new_message = None

    def get_username(self):
        return self.username

    def get_chat_message_controls(self):
        for message in self.messages:
            yield ChatMessage(message)

    def get_new_messages(self):
        for i in range(self.last_pos, len(self.messages)):
            yield ChatMessage(self.messages[i])
        self.last_pos = len(self.messages)

    def add_message(self, message: Message):
        self.messages.append(message)