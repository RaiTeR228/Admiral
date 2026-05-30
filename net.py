import sys
import time

try:
    import curses
except ImportError:
    sys.exit('платформа не поддерживается')

import psutil
from psutil._common import bytes2human

lineno = 0
win = curses.initscr()

def printl(line, highlight=False):
    """Тонкая обертка вокруг модуля curses."""
    global lineno
    try:
        if highlight:
            line += " " * (win.getmaxyx()[1] - len(line))
            win.addstr(lineno, 0, line, curses.A_REVERSE)
        else:
            win.addstr(lineno, 0, line, 0)
    except curses.error:
        lineno = 0
        win.refresh()
        raise
    else:
        lineno += 1

def poll(interval):
    """Необработанная статистика в интервале `interval`."""
    tot_before = psutil.net_io_counters()
    pnic_before = psutil.net_io_counters(pernic=True)
    # спим в течении `interval`
    time.sleep(interval)
    tot_after = psutil.net_io_counters()
    pnic_after = psutil.net_io_counters(pernic=True)
    return (tot_before, tot_after, pnic_before, pnic_after)

def refresh_window(tot_before, tot_after, pnic_before, pnic_after):
    """Вывод статистики на экран."""
    global lineno
    # всего
    printl("total bytes:           sent: %-10s   received: %s" % (
        bytes2human(tot_after.bytes_sent),
        bytes2human(tot_after.bytes_recv))
    )
    printl("total packets:         sent: %-10s   received: %s" % (
        tot_after.packets_sent, tot_after.packets_recv))

    # сведения об интерфейсе для каждой сети: 
    # отсортируем сетевые интерфейсы, первыми 
    # будут те, которые генерировали больше трафика.
    printl("")
    nic_names = list(pnic_after.keys())
    nic_names.sort(key=lambda x: sum(pnic_after[x]), reverse=True)
    for name in nic_names:
        stats_before = pnic_before[name]
        stats_after = pnic_after[name]
        templ = "%-15s %15s %15s"
        printl(templ % (name, "TOTAL", "PER-SEC"), highlight=True)
        printl(templ % (
            "bytes-sent",
            bytes2human(stats_after.bytes_sent),
            bytes2human(
                stats_after.bytes_sent - stats_before.bytes_sent) + '/s',
        ))
        printl(templ % (
            "bytes-recv",
            bytes2human(stats_after.bytes_recv),
            bytes2human(
                stats_after.bytes_recv - stats_before.bytes_recv) + '/s',
        ))
        printl(templ % (
            "pkts-sent",
            stats_after.packets_sent,
            stats_after.packets_sent - stats_before.packets_sent,
        ))
        printl(templ % (
            "pkts-recv",
            stats_after.packets_recv,
            stats_after.packets_recv - stats_before.packets_recv,
        ))
        printl("")
    win.refresh()
    lineno = 0

def setup():
    curses.start_color()
    curses.use_default_colors()
    for i in range(0, curses.COLORS):
        curses.init_pair(i + 1, i, -1)
    curses.endwin()
    win.nodelay(1)

def tear_down():
    win.keypad(0)
    curses.nocbreak()
    curses.echo()
    curses.endwin()

if __name__ == '__main__':
    setup()
    try:
        interval = 0
        while True:
            if win.getch() == ord('q'):
                break
            args = poll(interval)
            refresh_window(*args)
            interval = 0.5
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        tear_down()