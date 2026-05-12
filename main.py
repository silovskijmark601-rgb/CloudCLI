import os
import sys
import time
import threading
import datetime
import logging
import traceback
from typing import List, Optional, Dict

try:
    import yt_dlp
    import vlc
    from prompt_toolkit import PromptSession
    from prompt_toolkit.patch_stdout import patch_stdout
    from prompt_toolkit.shortcuts import print_formatted_text
    from prompt_toolkit.styles import Style
except ImportError:
    print("[!] Ошибка: Установи зависимости командой: uv add python-vlc yt-dlp prompt-toolkit")
    sys.exit(1)

VLC_ARGS = (
    '--no-video '
    '--quiet '
    '--network-caching=5000 '
    '--file-caching=5000 '
    '--clock-jitter=0 '
    '--clock-synchro=0'
)

UI_STYLE = Style.from_dict({
    'prefix': '#00ff00 bold',
    'status': '#ffff00 italic',
    'error': '#ff0000 bold',
    'track': '#00ffff',
    'info': '#888888',
})

class YDLQuietLogger:
    def debug(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass

YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'default_search': 'ytsearch',
    'noplaylist': True,
    'socket_timeout': 15,
    'retries': 5,
    'logger': YDLQuietLogger(),
}

class Track:
    def __init__(self, title: str, url: str, duration: int = 0, uploader: str = "Unknown"):
        self.title = title
        self.url = url
        self.duration = duration
        self.uploader = uploader
        self.added_at = datetime.datetime.now().strftime("%H:%M:%S")

    def get_duration_str(self) -> str:
        if not self.duration:
            return "??:??"
        return str(datetime.timedelta(seconds=self.duration))

    def __str__(self):
        return f"{self.title} [{self.get_duration_str()}] by {self.uploader}"

class MusicEngine:
    def __init__(self):
        self.instance = vlc.Instance(VLC_ARGS)
        self.player = self.instance.media_player_new()
        self.queue: List[Track] = []
        self.current_index: int = -1
        self.repeat_one: bool = False
        self.volume: int = 70
        self.player.audio_set_volume(self.volume)

    def add_to_queue(self, track: Track):
        self.queue.append(track)
        if not self.player.is_playing() and self.current_index == -1:
            self.play_index(0)

    def play_index(self, index: int):
        if 0 <= index < len(self.queue):
            self.current_index = index
            track = self.queue[index]
            media = self.instance.media_new(track.url)
            self.player.set_media(media)
            self.player.play()
            return track
        return None

    def play_next(self) -> Optional[Track]:
        if self.repeat_one and self.current_index != -1:
            return self.play_index(self.current_index)
        
        next_idx = self.current_index + 1
        if next_idx < len(self.queue):
            return self.play_index(next_idx)
        return None

    def play_prev(self) -> Optional[Track]:
        prev_idx = max(0, self.current_index - 1)
        if self.queue:
            return self.play_index(prev_idx)
        return None

    def toggle_pause(self) -> bool:
        is_playing = self.player.is_playing()
        if is_playing:
            self.player.pause()
        else:
            self.player.play()
        return not is_playing

    def stop(self):
        self.player.stop()

    def set_volume(self, value: int):
        self.volume = max(0, min(100, value))
        self.player.audio_set_volume(self.volume)

    def get_status(self) -> Dict:
        state = self.player.get_state()
        curr_track = self.queue[self.current_index] if self.current_index != -1 else None
        return {
            'state': str(state).split('.')[-1],
            'track': curr_track,
            'volume': self.volume,
            'repeat': self.repeat_one
        }

class CloudCLI:
    def __init__(self):
        self.engine = MusicEngine()
        self.session = PromptSession()
        self.is_running = True
        self.lock = threading.Lock()

    def print_ui(self, message: str, style_class: str = 'info'):
        with patch_stdout():
            print_formatted_text(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {message}", style=UI_STYLE)

    def search_and_add(self, query: str):
        self.print_ui(f"[*] Поиск в облаке: {query}...", 'status')
        try:
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(f"ytsearch1:{query} audio", download=False)
                if info and 'entries' in info and len(info['entries']) > 0:
                    entry = info['entries'][0]
                    new_track = Track(
                        title=entry.get('title', 'Unknown'),
                        url=entry.get('url'),
                        duration=entry.get('duration', 0),
                        uploader=entry.get('uploader', 'YouTube')
                    )
                    
                    with self.lock:
                        self.engine.add_to_queue(new_track)
                    
                    self.print_ui(f"[+] В очереди: {new_track.title}", 'track')
                else:
                    self.print_ui(f"[-] По запросу '{query}' ничего не найдено.", 'error')
                    
        except Exception:
            err_detail = traceback.format_exc().splitlines()[-1]
            self.print_ui(f"[!] Критическая ошибка сети: {err_detail}", 'error')

    def monitor_playback(self):
        while self.is_running:
            state = self.engine.player.get_state()
            if state == vlc.State.Ended:
                next_t = self.engine.play_next()
                if next_t:
                    self.print_ui(f"[>] Переход к: {next_t.title}", 'track')
            time.sleep(1)

    def show_help(self):
        help_text = """
        Доступные команды:
        /s <запрос>   - Поиск и добавление в очередь
        /p            - Пауза / Плей
        /n            - Следующий трек
        /b            - Предыдущий трек
        /v <0-100>    - Установить громкость
        /r            - Переключить повтор одного трека
        /q            - Показать текущую очередь
        /c            - Очистить консоль
        /exit         - Выход
        -------------------------------------------
        """
        print(help_text)

    def run(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"=== minnar>_< CloudCLI Music Engine v4.0 ===")
        self.show_help()

        threading.Thread(target=self.monitor_playback, daemon=True).start()

        while self.is_running:
            try:
                with patch_stdout():
                    cmd_raw = self.session.prompt("user > ").strip()
                
                if not cmd_raw:
                    continue

                if cmd_raw.startswith("/s"):
                    parts = cmd_raw.split(maxsplit=1)
                    if len(parts) > 1:
                        threading.Thread(
                            target=self.search_and_add, 
                            args=(parts[1].strip(),), 
                            daemon=True
                        ).start()
                    else:
                        self.print_ui("Введите название после /s", 'error')

                elif cmd_raw == "/p":
                    is_paused = self.engine.toggle_pause()
                    status = "ПАУЗА" if is_paused else "ИГРАЕТ"
                    self.print_ui(f"[*] Статус: {status}")

                elif cmd_raw == "/n":
                    self.engine.player.stop()
                    t = self.engine.play_next()
                    if t: self.print_ui(f"[>] Следующий: {t.title}")

                elif cmd_raw == "/b":
                    self.engine.player.stop()
                    t = self.engine.play_prev()
                    if t: self.print_ui(f"[<] Предыдущий: {t.title}")

                elif cmd_raw.startswith("/v"):
                    parts = cmd_raw.split()
                    if len(parts) > 1 and parts[1].isdigit():
                        val = int(parts[1])
                        self.engine.set_volume(val)
                        self.print_ui(f"[*] Громкость: {val}%")

                elif cmd_raw == "/r":
                    self.engine.repeat_one = not self.engine.repeat_one
                    mode = "ВКЛ" if self.engine.repeat_one else "ВЫКЛ"
                    self.print_ui(f"[*] Повтор одного трека: {mode}")

                elif cmd_raw == "/q":
                    self.print_ui("\n--- ТЕКУЩАЯ ОЧЕРЕДЬ ---")
                    if not self.engine.queue:
                        self.print_ui("    (пусто)")
                    for i, t in enumerate(self.engine.queue):
                        pointer = ">>" if i == self.engine.current_index else "  "
                        self.print_ui(f"{pointer} {i+1}. {t}")
                    self.print_ui("-----------------------\n")

                elif cmd_raw == "/c":
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("=== minnar>_< CloudCLI Music Engine v4.0 ===")

                elif cmd_raw == "/exit":
                    self.print_ui("[!] Завершение работы...")
                    self.engine.stop()
                    self.is_running = False

                else:
                    if not cmd_raw.startswith("/"):
                         threading.Thread(target=self.search_and_add, args=(cmd_raw,), daemon=True).start()

            except (KeyboardInterrupt, EOFError):
                self.is_running = False
                break
if __name__ == "__main__":
    if os.name == 'nt':
        vlc_path = r'C:\Program Files\VideoLAN\VLC'
        if os.path.exists(vlc_path):
            os.environ['PYTHON_VLC_MODULE_PATH'] = vlc_path
        else:
            print("[!] Предупреждение: VLC не найден в стандартной папке. Проверь установку 64-bit версии.")

    app = CloudCLI()
    try:
        app.run()
    except Exception as fatal:
        print(f"\n[FATAL ERROR]: {fatal}")
        input("Нажми Enter для выхода...")