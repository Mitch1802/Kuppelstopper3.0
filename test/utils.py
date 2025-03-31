import re, time

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

def write_konsole(app, text):
    if app.checked_Konsole.get():
        with open(app.LogFile, "a") as f:
            f.write(time.strftime('%X') + ' ' + text + '\n')
