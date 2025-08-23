import sys, os, threading, subprocess, shlex

class AudioManager:
    def __init__(self):
        self._proc = None      # thread or Popen or bool for pygame
        self._backend = None
        try:
            import pygame
            self._pygame = pygame
        except Exception:
            self._pygame = None

    def _is_wav(self, path: str) -> bool:
        return os.path.splitext(path)[1].lower() in (".wav", ".wave")

    def play(self, path: str):
        self.stop()
        if not path or not os.path.exists(path):
            return

        # 1) pygame (kann MP3/WAV, plattformunabhängig)
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
                # pygame fehlgeschlagen -> weiterprobieren
                pass

        # 2) Windows: winsound NUR für WAV
        if sys.platform.startswith("win") and self._is_wav(path):
            try:
                import winsound
                flags = winsound.SND_FILENAME | winsound.SND_NODEFAULT
                t = threading.Thread(target=winsound.PlaySound, args=(path, flags))
                t.daemon = True
                t.start()
                self._proc = t
                self._backend = "winsound"
                return
            except Exception:
                pass

        # 3) macOS: afplay
        if sys.platform == "darwin":
            try:
                self._proc = subprocess.Popen(["afplay", path])
                self._backend = "afplay"
                return
            except Exception:
                pass

        # 4) ffplay (FFmpeg) oder aplay (Linux)
        for cmd in (["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet"],
                    ["aplay"]):
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
            elif self._backend == "winsound":
                # Beendet laufende winsound-Wiedergabe
                import winsound
                winsound.PlaySound(None, winsound.SND_PURGE)
            elif self._backend in ("afplay", "ffplay", "aplay"):
                try:
                    self._proc.terminate()
                except Exception:
                    pass
        finally:
            self._proc = None
            self._backend = None
