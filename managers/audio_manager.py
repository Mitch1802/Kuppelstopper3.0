import sys, os, threading, subprocess


class AudioManager:
    def __init__(self):
        self._proc = None
        self._backend = None
        try:
            import pygame
            self._pygame = pygame
        except Exception:
            self._pygame = None

    def play(self, path: str):
        self.stop()
        if not path or not os.path.exists(path):
            return
        # Windows
        if sys.platform.startswith("win"):
            try:
                import winsound
                t = threading.Thread(target=winsound.PlaySound,
                                     args=(path, winsound.SND_FILENAME,))
                t.daemon = True
                t.start()
                self._proc = t
                self._backend = "winsound"
                return
            except Exception:
                pass
        # pygame
        if self._pygame:
            try:
                if not self._pygame.mixer.get_init():
                    self._pygame.mixer.init()
                self._pygame.mixer.music.load(path)
                self._pygame.mixer.music.play()
                self._backend = "pygame"
                self._proc = True
                return
            except Exception:
                pass
        # macOS
        if sys.platform == "darwin":
            try:
                self._proc = subprocess.Popen(["afplay", path])
                self._backend = "afplay"
                return
            except Exception:
                pass
        # ffplay / aplay
        for cmd in (["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet"], ["aplay"]):
            try:
                self._proc = subprocess.Popen(cmd + [path])
                self._backend = cmd[0]
                return
            except Exception:
                continue

    def stop(self):
        if not self._proc:
            return
        try:
            if self._backend == "pygame" and self._pygame:
                self._pygame.mixer.music.stop()
            elif self._backend in ("afplay", "ffplay", "aplay"):
                self._proc.terminate()
        except Exception:
            pass
        self._proc = None
        self._backend = None