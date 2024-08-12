import time
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.core.clipboard import Clipboard  # Importa o Clipboard para copiar textos

class ChatApp(App):
    def build(self):
        # Define a cor de fundo da janela
        Window.clearcolor = (0.15, 0.15, 0.15, 1)  # Cor de fundo da aplicação (cinza escuro)

        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Adiciona um ScrollView para permitir rolar o histórico de chat
        self.scrollview = ScrollView(size_hint=(1, 0.8), bar_width=10, bar_color=(0.7, 0.7, 0.7, 1))
        self.chat_container = GridLayout(cols=1, size_hint_y=None, spacing=10, padding=[10, 10, 10, 10])
        self.chat_container.bind(minimum_height=self.chat_container.setter('height'))

        self.scrollview.add_widget(self.chat_container)
        self.layout.add_widget(self.scrollview)

        # Personaliza o TextInput
        self.user_input = TextInput(size_hint_y=None, height=120, multiline=False,
                                    background_color=(0.2, 0.2, 0.2, 1), foreground_color=(1, 1, 1, 1),
                                    padding=(10, 10), font_size=20)
        self.layout.add_widget(self.user_input)

        # Personaliza o botão de enviar
        send_button = Button(text="Enviar", size_hint_y=None, height=100,
                             background_color=(0.3, 0.5, 0.7, 1), color=(1, 1, 1, 1),
                             font_size=24)
        send_button.bind(on_press=self.send_message)
        self.layout.add_widget(send_button)

        return self.layout

    def send_message(self, instance):
        user_message = self.user_input.text
        if user_message:
            self.add_message(f'Você: {user_message}', 'user')
            response = self.get_chatgpt_response(user_message)
            print("Resposta da função get_chatgpt_response:", response)  # Log da resposta
            if response is None or 'error' in response:
                self.add_message(f'Erro ao obter resposta: {response.get("error", "Resposta inesperada da API")}', 'error')
            else:
                self.add_message(f'ChatGPT: {response["choices"][0]["message"]["content"].strip()}', 'chatgpt')
            self.user_input.text = ''
            self.scrollview.scroll_to(self.chat_container.children[0])  # Rolagem automática para o mais recente

    def add_message(self, message, role):
        # Container horizontal para o label e o botão de copiar
        message_layout = BoxLayout(orientation='horizontal', size_hint_y=None, spacing=10)

        # Adiciona uma nova mensagem ao container de chat
        label = Label(text=message, size_hint_y=None, padding=(10, 10), halign='left', valign='middle',
                      text_size=(self.scrollview.width - 100, None))  # Reservando espaço para o botão
        label.bind(size=label.setter('text_size'))

        # Ajuste automático da altura com base no conteúdo
        label.texture_update()
        label.height = label.texture_size[1] + 20

        if role == 'user':
            label.color = (1, 1, 1, 1)  # Branco para mensagens do usuário
        elif role == 'chatgpt':
            label.color = (0.5, 0.8, 0.4, 1)  # Verde para mensagens do ChatGPT
        else:
            label.color = (1, 0.4, 0.4, 1)  # Vermelho para erros

        # Botão de copiar
        copy_button = Button(text="Copiar", size_hint_x=None, width=150, height=label.height,
                             background_color=(0.2, 0.6, 0.8, 1), color=(1, 1, 1, 1))
        copy_button.bind(on_press=lambda x: Clipboard.copy(message))

        # Adiciona o label e o botão de copiar ao layout
        message_layout.add_widget(label)
        message_layout.add_widget(copy_button)

        # Adiciona o layout da mensagem ao container principal
        self.chat_container.add_widget(message_layout)

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
            'max_tokens': 4096
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
                    return response.json()  # Retorna o JSON se a requisição for bem-sucedida
                else:
                    # Retorna uma mensagem de erro se o status da resposta não for 200
                    return {'error': f'Erro na API: {response.status_code} - {response.text}'}
            except requests.RequestException as e:
                print(f"Exceção durante a requisição: {e}")
                return {'error': 'Erro ao tentar se comunicar com a API.'}

        return {'error': 'Número máximo de tentativas excedido. Tente novamente mais tarde.'}

if __name__ == "__main__":
    ChatApp().run()