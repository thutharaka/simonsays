import subprocess


def get_current_desktop() -> int:
    """ Returns current desktop ID """
    res = subprocess.run(['xprop', '-root', '_NET_CURRENT_DESKTOP'],
                         capture_output=True, text=True, check=True)
    # xD
    return int(res.stdout.split("=")[1].strip())


def get_stacking_list() -> list[int]:
    """ Returns a list of ints representing xorg window hex codes in int """
    res = subprocess.run(['xprop', '-root', '_NET_CLIENT_LIST_STACKING'],
                         capture_output=True, text=True, check=True)
    # xD
    stacking_list_str = res.stdout.split("window id #")[1].split(',')
    stacking_list = [ int(id, 16) for id in stacking_list_str ]
    # Output stacking list is higher precedence -> lower precedence
    return stacking_list[::-1]


def get_current_windows() -> list[dict]:
    current_desktop = get_current_desktop()
    res = subprocess.run(['wmctrl', '-lGp'], capture_output=True, text=True, check=True)
    current_windows = []
    for window in res.stdout.split('\n'):
        if window == "": continue
        # TODO games can be handled here, we can extract window titles
        window_hex, desktop, pid, _, __, w, h = window.split()[:7]
        if int(desktop) != current_desktop: continue

        # We don't use x,y values from wmctrl because that's apparently a 
        # relative value, so we're forced to invoke xwininfo instead
        abs_xy_res = subprocess.run(['xwininfo', '-id', window_hex], capture_output=True, text=True, check=True)
        abs_x = int(abs_xy_res.stdout.split('\n')[3].split(":")[1])
        abs_y = int(abs_xy_res.stdout.split('\n')[4].split(":")[1])

        current_windows.append({
            "xorg_hex": int(window_hex, 16),
            "pid": int(pid),
            "column_min": abs_x,
            "column_max": abs_x + int(w),
            "row_min": abs_y,
            "row_max": abs_y + int(h)
        })
    return current_windows


def get_window_at_coords(x: int, y: int, windows, stacking_list) -> tuple:
    """ Returns the xorg hex, PID of the window at coords """
    potential_windows = []
    for window in windows:
        is_within_window = (
            x >= window["column_min"] and x <= window["column_max"] and
            y >= window["row_min"] and y <= window["row_max"]
        )
        if is_within_window:
            potential_windows.append((window["xorg_hex"], window["pid"]))

    for stacking_hex in stacking_list:
        for hex, pid in potential_windows:
            if hex == stacking_hex:
                return hex, pid

    return None
    # raise Exception("Couldn't find a window at coords")


def get_window_title(hex: int) -> str:
    res = subprocess.run(['xprop', '-id', str(hex), '_NET_WM_NAME'],
                         capture_output=True, text=True, check=True)
    # xD
    return res.stdout.split("=")[1].strip()


def notify(title: str, msg: str):
    subprocess.run([
        'notify-send', title, msg #, '--replace-id', '42069'
    ])


def simon_disappoint():
    """ Simon is disappointed """
    subprocess.Popen(['google-chrome-stable', '127.0.0.1:5000/simonsays'])


def toggle_wallpaper():
    subprocess.Popen(['bash', '/home/ian/lib/bin/simonsays/analyzer/temp_wallpaper.sh'])

# TODO do not kill if Simon says tab is currently active
