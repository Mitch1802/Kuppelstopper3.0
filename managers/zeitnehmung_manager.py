import time
import threading

class ZeitManager:
    """
    ZeitManager: kümmert sich um die Stoppuhr-Logik für zwei Bahnen.

    - start(lane1=True, lane2=True)
    - stop_lane(1 oder 2)
    - stop_all()
    - reset()
    - is_running() -> bool
    - get_elapsed_seconds() -> (sec1, sec2)
    - get_times_strings() -> (str1, str2)
    - on_tick(callback) -> ruft callback(z1:str, z2:str) ~20x pro Sekunde auf (separater Thread)
    """

    def __init__(self):
        # Startzeitpunkte (perf_counter), None = nicht aktiv
        self._t0_b1 = None
        self._t0_b2 = None

        # akkumulierte Sekunden pro Bahn (falls gestoppt + neu gestartet)
        self._acc_b1 = 0.0
        self._acc_b2 = 0.0

        # läuft mindestens eine Bahn?
        self._running = False

        # optionaler Callback
        self._tick_callback = None
        self._tick_thread = None
        self._tick_stop = threading.Event()

    # ========= Public API =========

    def start(self, lane1: bool = True, lane2: bool = True):
        """Startet eine oder beide Bahnen."""
        now = time.perf_counter()
        if lane1:
            self._t0_b1 = now
            self._acc_b1 = 0.0
        if lane2:
            self._t0_b2 = now
            self._acc_b2 = 0.0
        self._running = lane1 or lane2
        self._start_tick_thread()

    def stop_lane(self, lane: int):
        """Stoppt eine einzelne Bahn (1 oder 2)."""
        now = time.perf_counter()
        if lane == 1 and self._t0_b1 is not None:
            self._acc_b1 += now - self._t0_b1
            self._t0_b1 = None
        elif lane == 2 and self._t0_b2 is not None:
            self._acc_b2 += now - self._t0_b2
            self._t0_b2 = None
        self._check_running_state()

    def stop_all(self):
        """Stoppt beide Bahnen."""
        now = time.perf_counter()
        if self._t0_b1 is not None:
            self._acc_b1 += now - self._t0_b1
            self._t0_b1 = None
        if self._t0_b2 is not None:
            self._acc_b2 += now - self._t0_b2
            self._t0_b2 = None
        self._running = False
        self._stop_tick_thread()

    def reset(self):
        """Setzt alle Zeiten zurück."""
        self._t0_b1 = None
        self._t0_b2 = None
        self._acc_b1 = 0.0
        self._acc_b2 = 0.0
        self._running = False
        self._stop_tick_thread()

    def is_running(self) -> bool:
        return self._running

    def get_elapsed_seconds(self) -> tuple[float | None, float | None]:
        """Gibt die aktuellen Sekundenwerte beider Bahnen zurück (oder None)."""
        now = time.perf_counter()
        sec1 = self._acc_b1 + (now - self._t0_b1) if self._t0_b1 is not None else (self._acc_b1 if self._acc_b1 > 0 else None)
        sec2 = self._acc_b2 + (now - self._t0_b2) if self._t0_b2 is not None else (self._acc_b2 if self._acc_b2 > 0 else None)
        return sec1, sec2

    def get_times_strings(self) -> tuple[str, str]:
        """Formatiert mm:ss:cc (Hundertstel)."""
        return (self._fmt_time(self.get_elapsed_seconds()[0]),
                self._fmt_time(self.get_elapsed_seconds()[1]))

    def on_tick(self, callback):
        """Setzt einen Callback, der zyklisch (ca. 20x/s) Zeiten als Strings liefert."""
        self._tick_callback = callback
        if self._running:
            self._start_tick_thread()

    # ========= intern =========

    def _check_running_state(self):
        self._running = (self._t0_b1 is not None) or (self._t0_b2 is not None)
        if not self._running:
            self._stop_tick_thread()

    def _fmt_time(self, seconds: float | None) -> str:
        if seconds is None:
            return "00:00:00"
        if seconds < 0:
            seconds = 0.0
        m = int(seconds // 60)
        s = int(seconds % 60)
        cs = int((seconds - int(seconds)) * 100)  # Hundertstel
        return f"{m:02d}:{s:02d}:{cs:02d}"

    def _start_tick_thread(self):
        if self._tick_callback is None or self._tick_thread is not None:
            return
        self._tick_stop.clear()
        self._tick_thread = threading.Thread(target=self._tick_loop, daemon=True)
        self._tick_thread.start()

    def _stop_tick_thread(self):
        if self._tick_thread is not None:
            self._tick_stop.set()
            self._tick_thread = None

    def _tick_loop(self):
        while not self._tick_stop.wait(0.05):  # alle 50 ms
            if not self._running:
                break
            if self._tick_callback:
                try:
                    z1, z2 = self.get_times_strings()
                    self._tick_callback(z1, z2)
                except Exception:
                    pass
