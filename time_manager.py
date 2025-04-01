import time
from datetime import datetime

def update_time_1(app):
    if app.time_is_running_1:
        elapsed_time = time.time() - app.start_time_1
        dt = datetime.fromtimestamp(elapsed_time).strftime('%M:%S:%f')[:-4]
        app.root.T1.configure(text=dt)
        app.anzeige.Z1.configure(text=dt)
        app.root.T1.after(50, lambda: update_time_1(app))
    else:
        app.stop_time_1 = time.time()

def update_time_2(app):
    if app.time_is_running_2:
        elapsed_time = time.time() - app.start_time_2
        dt = datetime.fromtimestamp(elapsed_time).strftime('%M:%S:%f')[:-4]
        app.root.T2.configure(text=dt)
        app.anzeige.Z2.configure(text=dt)
        app.root.T2.after(50, lambda: update_time_2(app))
    else:
        app.stop_time_2 = time.time()

def addiere_fehler_zur_zeit(zeit, fehler):
    t = zeit.split(':')
    t_minute = int(t[0])
    t_sekunden = int(t[1])
    t_milisekunden = int(t[2])
    t_fehler = int(fehler)
    t_sekunden += t_fehler
    if t_sekunden > 59:
        t_sekunden -= 60
        t_minute += 1
    return f"{t_minute:02}:{t_sekunden:02}:{t_milisekunden:02}"

def bestzeit_platzierung_berechnen(app):
    # Berechne hier die Platzierung basierend auf den erfassten Zeiten.
    # Durchlaufe app.Durchgänge, aktualisiere die Felder und rufe ggfs. Zeichnungsfunktionen auf.
    pass

def reset_timers(app):
    app.root.T1.configure(text='00:00:00')
    app.root.T2.configure(text='00:00:00')
    app.anzeige.Z1.configure(text='00:00:00')
    app.anzeige.Z2.configure(text='00:00:00')
