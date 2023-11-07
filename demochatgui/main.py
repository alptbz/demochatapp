import json
import time
import tkinter
from threading import Thread
from tkinter import *
from tkinter import ttk, messagebox
import requests

import endpoints
import special_widgets


class ChatAppGui:

    def __init__(self, endpoint_manager: endpoints.EndpointManager):
        self.endpoint_manager = endpoint_manager
        self.data = []
        self.token = ""
        self.pull_thread : Thread = None
        self.stop_thread = False
        self.last_id = 0
        self.message_store = []
        self.chathistory_position = -1
        self.selected_other = None
        self._init_gui()


    def run(self):
        self.root.mainloop()

    def _init_gui(self):
        self.root = Tk()
        self.root.title("ChatApp")
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        frm = ttk.Frame(self.root, padding=10)
        frm.grid()
        tkinter.Label(frm, text="Username:").grid(column=0, row=0)
        self.usernamebox_content = tkinter.StringVar()
        self.usernamebox = tkinter.Entry(frm, width=20, textvariable=self.usernamebox_content)
        self.usernamebox_content.set("max")
        self.usernamebox.grid(column=1, row=0)

        tkinter.Label(frm, text="Password:").grid(column=2, row=0)
        self.passwordbox_content = tkinter.StringVar()
        self.passwordbox = tkinter.Entry(frm, width=20, show="*", textvariable=self.passwordbox_content)
        self.passwordbox_content.set("1234")
        self.passwordbox.grid(column=3, row=0)

        self.loginbutton = tkinter.Button(frm, text="Login", command=self._login)
        self.loginbutton.grid(column=4, row=0)

        tkinter.Label(frm, text="Conversation:").grid(column=0, row=1)
        self.conversation_combobox_selected = tkinter.StringVar()
        self.conversation_combobox_selected.trace('w', self._on_selected_conversation_change)
        self.conversation_combobox = ttk.Combobox(frm, textvariable=self.conversation_combobox_selected)
        self.conversation_combobox.grid(column=1, row=1, columnspan=1)

        self.chathistorybox = special_widgets.ReadOnlyText(frm, width=80, height=20, wrap=tkinter.WORD)
        self.chathistorybox.grid(column=0, row=2, columnspan=4)

        self.newmessagebox = tkinter.Entry(frm, width=40)
        self.newmessagebox.grid(column=1, row=3, columnspan=2)

        self.newmessagebox.bind('<Return>', self._on_messagebox_enter)

        self.send_button = tkinter.Button(frm, text="Send", command=self._send_message)
        self.send_button.grid(column=3, row=3)
        self._disable_all_input_ui()

    def _disable_all_input_ui(self):
        self.newmessagebox["state"] = DISABLED
        self.conversation_combobox["state"] = DISABLED
        self.send_button["state"] = DISABLED

    def _send_message(self):
        message = self.newmessagebox.get()
        receiver = self.conversation_combobox_selected.get()
        self.newmessagebox.delete(0, END)
        fire_and_forget = Thread(target=self._send_message_task, args=(receiver, message))
        fire_and_forget.start()

    def _send_message_task(self, receiver, message):
        send_req = requests.post(self.endpoint_manager.send(), headers=self._get_headers(), json={"to": receiver, "message": message})
        if send_req.status_code != 200:
            messagebox.showinfo(master=self.root, message=f"message send failure ({send_req.status_code}, {send_req.content})")

    def _login(self):
        if self.pull_thread is not None:
            self.stop_thread = True
            self._disable_all_input_ui()
            self.conversation_combobox.set('')
            self.selected_other = None
            self.message_store = []
            self.last_id = 0
            time.sleep(1)
        resp = requests.post(self.endpoint_manager.login(), json={
            "username": self.usernamebox.get(), "password": self.passwordbox.get()})
        if resp.status_code != 200:
            errmsg = f"Login failure ({resp.status_code}, {resp.content})"
            messagebox.showinfo(master=self.root, message=errmsg)
            print(errmsg)

        else:
            self.token = json.loads(resp.content)["data"]["token"]
            self.conversation_combobox["state"] = NORMAL
            self.pull_thread = Thread(target=self._pull_thread)
            self.stop_thread = False
            self.pull_thread.start()
            print("Login successfull")


    def _on_messagebox_enter(self, event):
        self._send_message()

    def _on_selected_conversation_change(self, index, value, op):
        self.selected_other = self.conversation_combobox_selected.get()
        self.chathistory_position = -1
        self.chathistorybox.delete(0.0, END)
        self._update_chathistory()
        self.newmessagebox["state"] = NORMAL
        self.send_button["state"] = NORMAL
        pass

    def _update_chathistory(self):
        if self.selected_other is None:
            return
        messages = [m for m in self.message_store if m["sender"] == self.selected_other or m["receiver"] == self.selected_other]
        if len(messages) == 0:
            return
        for m in messages:
            if m["id"] > self.chathistory_position:
                self.chathistorybox.insert(END, f'{m["sender"]} ({m["created"]}): {m["message"]}\n')
        self.chathistory_position = max([x["id"] for x in messages])
        self.chathistorybox.see(END)


    def _on_closing(self):
        self.stop_thread = True
        time.sleep(2)
        self.root.destroy()

    def _get_headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    def _pull_thread(self):
        while not self.stop_thread:
            conversations_resp = requests.get(self.endpoint_manager.conversations(), headers=self._get_headers())
            self.conversation_combobox['values'] = json.loads(conversations_resp.content)

            new_messages_resp = requests.get(self.endpoint_manager.conversation_updates(self.last_id), headers=self._get_headers())
            new_messages = json.loads(new_messages_resp.content)
            if len(new_messages) > 0:
                self.message_store.extend(new_messages)
                self.last_id = max([x["id"] for x in new_messages])
                print(f"Received {len(new_messages)} new messages")
                self._update_chathistory()
            time.sleep(1)
        pass


if __name__ == '__main__':
    endpoint_manager = endpoints.EndpointManager("http://127.0.0.1:5000")
    ui = ChatAppGui(endpoint_manager)
    ui.run()

