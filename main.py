import time
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout

class ChatApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')

        # Adiciona um ScrollView para permitir rolar o histórico de chat
        self.scrollview = ScrollView(size_hint=(1, 0.8))
        self.chat_container = GridLayout(cols=1, size_hint_y=None)
        self.chat_container.bind(minimum_height=self.chat_container.setter('height'))

        self.scrollview.add_widget(self.chat_container)
        self.layout.add_widget(self.scrollview)

        self.user_input = TextInput(size_hint_y=None, height=120, multiline=False, padding=(10, 10))
        self.layout.add_widget(self.user_input)

        send_button = Button(text="Enviar", size_hint_y=None, height=100)
        send_button.bind(on_press=self.send_message)
        self.layout.add_widget(send_button)

        return self.layout

    def send_message(self, instance):
        user_message = self.user_input.text
        if user_message:
            self.add_message(f'Você: {user_message}', 'user')
            response = self.get_chatgpt_response(user_message)
            print("Resposta da função get_chatgpt_response:", response)  # Log da resposta
            if 'choices' in response:
                self.add_message(f'ChatGPT: {response["choices"][0]["message"]["content"].strip()}', 'chatgpt')
            else:
                self.add_message(f'Erro ao obter resposta da API: {response}', 'error')
            self.user_input.text = ''
            self.scrollview.scroll_to(self.chat_container.children[0])  # Rolagem automática para o mais recente

    def add_message(self, message, role):
        # Adiciona uma nova mensagem ao container de chat
        label = Label(text=message, size_hint_y=None, height=40, padding=(10, 10))
        if role == 'user':
            label.color = (1, 1, 1, 1)  # Branco para mensagens do usuário
        elif role == 'chatgpt':
            label.color = (0, 1, 0, 1)  # Verde para mensagens do ChatGPT
        else:
            label.color = (1, 0, 0, 1)  # Vermelho para erros

        self.chat_container.add_widget(label)

    def get_chatgpt_response(self, prompt):
        api_key = 'CHAVE-API'  # Substitua pela sua chave de API real
        url = 'https://api.openai.com/v1/chat/completions'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        data = {
            'model': 'gpt-3.5-turbo',
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': 150
        }

        max_retries = 5
        for attempt in range(max_retries):
            try:
                response = requests.post(url, headers=headers, json=data)
                print(f"Tentativa {attempt + 1}, status da resposta: {response.status_code}")
                if response.status_code == 429:
                    wait_time = 2 ** attempt  # Backoff exponencial: 2^attempt segundos
                    print(f'Too Many Requests: tentando novamente em {wait_time} segundos...')
                    time.sleep(wait_time)
                    continue
                elif response.status_code == 200:
                    return response.json()
                else:
                    return {'error': f'Erro na API: {response.status_code} - {response.json()}'}
            except requests.RequestException as e:
                print(f"Exceção durante a requisição: {e}")
                return {'error': 'Erro ao tentar se comunicar com a API.'}
        
        return {'error': 'Número máximo de tentativas excedido. Tente novamente mais tarde.'}

if __name__ == "__main__":
    ChatApp().run()