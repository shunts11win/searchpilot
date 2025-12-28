from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
import requests
import time
import random
import threading

__version__ = '3.2'

class SearchPilotApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.running = False
        self.count = 0
        self.limit = 30
        self.mode = 2
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml',
            'Accept-Language': 'ja,en-US;q=0.9',
        })
    
    def build(self):
        # メインレイアウト
        main = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # タイトル
        title = Label(
            text='SearchPilot Mobile',
            size_hint=(1, 0.1),
            font_size='24sp',
            bold=True,
            color=(0.2, 0.8, 1, 1)
        )
        main.add_widget(title)
        
        # 検索回数スライダー
        limit_box = BoxLayout(orientation='vertical', size_hint=(1, 0.15), spacing=5)
        self.limit_label = Label(
            text=f'検索回数: {self.limit}',
            size_hint=(1, 0.5),
            font_size='16sp'
        )
        limit_box.add_widget(self.limit_label)
        
        self.limit_slider = Slider(
            min=1,
            max=100,
            value=30,
            step=1,
            size_hint=(1, 0.5)
        )
        self.limit_slider.bind(value=self.on_limit_change)
        limit_box.add_widget(self.limit_slider)
        main.add_widget(limit_box)
        
        # 速度モード選択
        mode_box = BoxLayout(orientation='vertical', size_hint=(1, 0.15), spacing=5)
        mode_label = Label(
            text='速度モード:',
            size_hint=(1, 0.3),
            font_size='16sp'
        )
        mode_box.add_widget(mode_label)
        
        mode_buttons = BoxLayout(orientation='horizontal', size_hint=(1, 0.7), spacing=10)
        self.mode_btns = []
        for i, name in enumerate(['高速', '標準', '慎重'], 1):
            btn = ToggleButton(
                text=name,
                group='mode',
                state='down' if i == 2 else 'normal',
                font_size='14sp'
            )
            btn.bind(on_press=lambda x, mode=i: self.set_mode(mode))
            mode_buttons.add_widget(btn)
            self.mode_btns.append(btn)
        mode_box.add_widget(mode_buttons)
        main.add_widget(mode_box)
        
        # TURBOモードトグル
        self.turbo_btn = ToggleButton(
            text='🚀 TURBOモード',
            size_hint=(1, 0.08),
            font_size='16sp',
            background_color=(1, 0.3, 0.3, 1)
        )
        self.turbo_btn.bind(on_press=self.toggle_turbo)
        main.add_widget(self.turbo_btn)
        
        # 開始/停止ボタン
        self.start_btn = Button(
            text='▶ 開始',
            size_hint=(1, 0.1),
            font_size='20sp',
            background_color=(0.2, 0.8, 0.2, 1)
        )
        self.start_btn.bind(on_press=self.toggle_search)
        main.add_widget(self.start_btn)
        
        # ステータス表示
        self.status_label = Label(
            text='待機中',
            size_hint=(1, 0.08),
            font_size='14sp',
            color=(0.8, 0.8, 0.8, 1)
        )
        main.add_widget(self.status_label)
        
        # ログ表示エリア
        log_label = Label(
            text='検索ログ:',
            size_hint=(1, 0.05),
            font_size='14sp'
        )
        main.add_widget(log_label)
        
        scroll = ScrollView(size_hint=(1, 0.39))
        self.log_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.log_layout.bind(minimum_height=self.log_layout.setter('height'))
        scroll.add_widget(self.log_layout)
        main.add_widget(scroll)
        
        return main
    
    def on_limit_change(self, instance, value):
        self.limit = int(value)
        self.limit_label.text = f'検索回数: {self.limit}'
    
    def set_mode(self, mode):
        self.mode = mode
    
    def toggle_turbo(self, instance):
        if instance.state == 'down':
            self.limit = 999
            self.mode = 0
            self.limit_slider.value = 100
            self.limit_label.text = '検索回数: 無制限 (TURBO)'
            for btn in self.mode_btns:
                btn.disabled = True
        else:
            self.limit = 30
            self.mode = 2
            self.limit_slider.value = 30
            self.limit_label.text = f'検索回数: {self.limit}'
            for btn in self.mode_btns:
                btn.disabled = False
    
    def toggle_search(self, instance):
        if self.running:
            self.running = False
            self.start_btn.text = '▶ 開始'
            self.start_btn.background_color = (0.2, 0.8, 0.2, 1)
            self.status_label.text = '停止中...'
        else:
            self.running = True
            self.count = 0
            self.start_btn.text = '■ 停止'
            self.start_btn.background_color = (0.8, 0.2, 0.2, 1)
            self.status_label.text = '実行中...'
            self.log_layout.clear_widgets()
            threading.Thread(target=self.run_search, daemon=True).start()
    
    def add_log(self, text, color=(1, 1, 1, 1)):
        def update(dt):
            log = Label(
                text=text,
                size_hint_y=None,
                height=30,
                font_size='12sp',
                color=color
            )
            self.log_layout.add_widget(log)
        Clock.schedule_once(update)
    
    def update_status(self, text):
        Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', text))
    
    def get_wikipedia_title(self):
        try:
            params = {"action": "query", "format": "json", "list": "random", 
                     "rnnamespace": 0, "rnlimit": 1}
            data = requests.get(
                random.choice(["https://ja.wikipedia.org/w/api.php", 
                             "https://en.wikipedia.org/w/api.php"]), 
                params=params, timeout=5
            ).json()
            title = data['query']['random'][0]['title'].strip()
            if 1 <= len(title) <= 100:
                return title
        except:
            pass
        return random.choice(["Computer", "Music", "History", "Technology"])
    
    def run_search(self):
        while self.running and self.count < self.limit:
            self.count += 1
            query = self.get_wikipedia_title()
            
            self.update_status(f'検索中: {query} ({self.count}/{self.limit})')
            self.add_log(f'[{self.count}] 検索: {query}', (0.5, 1, 1, 1))
            
            start = time.time()
            try:
                turbo = self.mode == 0
                speed = [(0.05, 0.1), (0.3, 3.0), (0.5, 5.0), (1.0, 8.0)][self.mode]
                total = speed[0] + (len(query) - 2) * ((speed[1] - speed[0]) / 48)
                typing_delay = max(speed[0], min(speed[1], total))
                time.sleep(typing_delay)
                
                response = self.session.get(
                    'https://www.bing.com/search',
                    params={'q': query, 'form': 'QBLH'},
                    timeout=10
                )
                
                search_time = time.time() - start
                
                if response.status_code == 200:
                    self.add_log(f'  ✓ 成功 ({search_time:.1f}秒)', (0.5, 1, 0.5, 1))
                else:
                    self.add_log(f'  ! 警告: {response.status_code}', (1, 1, 0.5, 1))
                
            except Exception as e:
                self.add_log(f'  ✗ エラー: {str(e)[:30]}', (1, 0.5, 0.5, 1))
            
            if self.count >= self.limit:
                self.running = False
                self.update_status(f'完了！ {self.count}回の検索を実行')
                Clock.schedule_once(lambda dt: self.reset_button())
                break
            
            wait = random.uniform(1, 2) if self.mode == 0 else random.uniform(5, 8)
            self.update_status(f'待機中... ({wait:.1f}秒)')
            time.sleep(wait)
    
    def reset_button(self):
        self.start_btn.text = '▶ 開始'
        self.start_btn.background_color = (0.2, 0.8, 0.2, 1)

if __name__ == '__main__':
    SearchPilotApp().run()
