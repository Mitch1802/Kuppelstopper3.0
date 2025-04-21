import re, time
import events, config

def validate_time(test_str):
    pattern_str = r'^\d{2}:\d{2}:\d{2}$'
    if re.match(pattern_str, test_str):
        parts = test_str.split(':')
        if int(parts[0]) > 59 or int(parts[1]) > 59:
            return False
        return True
    return False

def validate_number(test_str):
    return test_str.isdigit()

def is_number(text):
    try:
        float(text)
        return True
    except ValueError:
        return False

def sort_time(app, timeList):
    if timeList['typ'] == app.TYP_GD  or timeList['typ'] == app.TYP_DW:
        if timeList['bestzeitinklfehler'] == '':
            return timeList['typ'], '59', '59', '99'
        else:
            split_up = timeList['bestzeitinklfehler'].split(':')
            return timeList['typ'], split_up[0], split_up[1], split_up[2]
    else:
        if timeList['bestzeitinklfehler'] == '':
            return timeList['typ'], timeList['dg'], '59', '59', '99'
        else:
            split_up = timeList['bestzeitinklfehler'].split(':')
            return timeList['typ'], timeList['dg'], split_up[0], split_up[1], split_up[2]

def sort_time_by_row(timeList):
    return timeList['typ'], timeList['row']

def sort_time_by_besttime(timeList):
    if timeList['bestzeit'] != '':
        return events.addiere_fehler_zur_zeit(timeList['bestzeit'], str(timeList['fehlerbest']))
    else:
        return '59:59:99'

def write_konsole(app, text):
    if app.checked_Konsole.get():
        with open(app.LogFile, "a") as f:
            f.write(time.strftime('%X') + ' ' + text + '\n')

def konvertiere_array(app, dg_nummer, wettkampfgruppe, typ, row, column, hinweis):
    if str(dg_nummer) not in app.DGNumbers:
        app.DGNumbers.append(str(dg_nummer))
    
    groupdict = {
        'wettkampfgruppe': wettkampfgruppe,
        'hinweis': hinweis,             # Hinweis für Platzierungsposition zb GD_1
        'platzierung': 0,
        'zeit1': '',
        'fehler1': 0,
        'zeit2': '',
        'fehler2': 0,
        'bestzeit': '',
        'fehlerbest': 0,
        'bestzeitinklfehler':'',
        'typ': typ,                     # Art  (Grunddurchgang, Viertelfinale, ...)
        'dg': dg_nummer,                # Nummer des Durchganges
        'row': row,                     # Reihe von Name
        'column': column,               # Spalte von Name           
    }
    app.Durchgänge.append(groupdict)
