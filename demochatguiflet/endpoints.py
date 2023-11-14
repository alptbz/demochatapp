class EndpointManager:

    def __init__(self, endpoint_url):
        self.endpoint_url = endpoint_url

    def send(self):
        return f'{self.endpoint_url}/send'

    def login(self):
        return f'{self.endpoint_url}/users/login'

    def conversations(self):
        return f'{self.endpoint_url}/conversations'

    def conversation_updates(self, last_id):
        return f'{self.endpoint_url}/conversations/updates/{last_id}'


