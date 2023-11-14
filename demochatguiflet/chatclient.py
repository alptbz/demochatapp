import json
import time
from threading import Thread
from typing import List

import requests

from classes import ChatConversation, Message, ChatMessage
from endpoints import EndpointManager


class ChatClient:

    def __init__(self, endpoint_url: str):
        self.token: str = None
        self.stop_thread: bool = True
        self.pull_thread: Thread = None
        self.conversations: List[ChatConversation] = []
        self.endpoint_url = endpoint_url
        self.endpoint_manager = EndpointManager(endpoint_url)
        self.username = None
        self.active_conversation : ChatConversation = None
        self.message_store = []
        self.last_id: int = 0
        self.on_new_message = None
        self.on_new_userlist = None

    def get_active_conversation_chat_messages(self):
        if self.active_conversation is None:
            return []
        return self.active_conversation.get_chat_message_controls()

    def login(self, username, password):
        resp = requests.post(self.endpoint_manager.login(), json={
            "username": username, "password": password})
        if resp.status_code != 200:
            errmsg = f"Login failure ({resp.status_code}, {resp.content})"
            print(errmsg)
            return False
        else:
            self.username = username
            self.token = json.loads(resp.content)["data"]["token"]
            self.pull_thread = Thread(target=self._pull_thread)
            self.stop_thread = False
            self.pull_thread.start()
            print("Login successfull")
            return True

    def __add_or_update_conversation(self, username) -> None:
        if self.__get_conversation(username) is None:
            self.conversations.append(ChatConversation(username))
            self.__fire_on_new_user_list()
            time.sleep(0.2)

    def __get_conversation(self, username) -> ChatConversation:
        c = [c for c in self.conversations if c.get_username() == username]
        if len(c) == 1:
            return c[0]
        return None

    def is_login(self):
        return self.username is not None

    def __fire_on_new_user_list(self):
        if self.on_new_userlist is not None:
            self.on_new_userlist([c.get_username() for c in self.conversations])

    def __fire_on_new_message(self, message: Message):
        if self.on_new_message is not None and self.active_conversation is not None:
            self.on_new_message(ChatMessage(message))

    def __distribute_messages(self, new_messages):
        for m in new_messages:
            relevant_username = m["sender"]
            if relevant_username == self.username:
                relevant_username = m["receiver"]
            c = self.__get_conversation(relevant_username)
            mc = Message(m["sender"], m["receiver"], m["message"], m["created"])
            c.add_message(mc)
            if c == self.active_conversation:
                self.__fire_on_new_message(mc)

    def _pull_thread(self):
        while not self.stop_thread:
            conversations_resp = requests.get(self.endpoint_manager.conversations(), headers=self._get_headers())
            usernames = json.loads(conversations_resp.content)
            for username in usernames:
                self.__add_or_update_conversation(username)

            new_messages_resp = requests.get(self.endpoint_manager.conversation_updates(self.last_id), headers=self._get_headers())
            new_messages = json.loads(new_messages_resp.content)
            if len(new_messages) > 0:
                self.message_store.extend(new_messages)
                self.__distribute_messages(new_messages)
                self.last_id = max([x["id"] for x in new_messages])
                print(f"Received {len(new_messages)} new messages")
            time.sleep(1)
        pass

    def _get_headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    def send_message(self, message) -> None:
        if self.active_conversation is None:
            return
        send_req = requests.post(self.endpoint_manager.send(), headers=self._get_headers(),
                                 json={"to": self.active_conversation.get_username(), "message": message})
        if send_req.status_code != 200:
            print(f"message send failure ({send_req.status_code}, {send_req.content})")

    def select_conversation(self, username: str):
        self.active_conversation = self.__get_conversation(username)


