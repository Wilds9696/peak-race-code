import time
import random
import os
import sys

# ─── Konfigurasi ───────────────────────────────────────────────────────────────
TRACK_WIDTH  = 60   # panjang lintasan (karakter)
FINISH_LINE  = TRACK_WIDTH - 12
FRAME_DELAY  = 0.07

# Kecepatan base sama, tapi ada noise acak setiap frame
BASE_SPEED   = 1
MAX_NOISE    = 3    # seberapa acak per langkah

# ─── ASCII Art Mobil ───────────────────────────────────────────────────────────
def car_carry(label="MBG (CARRY)"):
    w = max(len(label), 9)
    top  = " _" + "_" * w + "_ "
    mid  = "| " + label.center(w) + " |)"
    bot  = "|~∿∿@∿∿∿∿∿@∿~|)"
    return [top, mid, bot]

def car_f1(label="  MOB F1  "):
    w = max(len(label), 9)
    top  = "  __" + "_" * w + "___  "
    mid  = "=| " + label.center(w) + "  |>"
    bot  = " O‾‾‾‾‾‾‾‾‾‾‾‾O "
    return [top, mid, bot]

# ─── Render Lintasan ───────────────────────────────────────────────────────────
COLORS = {
    "yellow": "\033[93m",
    "cyan"  : "\033[96m",
    "green" : "\033[92m",
    "red"   : "\033[91m",
    "white" : "\033[97m",
    "bold"  : "\033[1m",
    "reset" : "\033[0m",
    "gray"  : "\033[90m",
}

def clr(text, *codes):
    return "".join(COLORS.get(c, "") for c in codes) + text + COLORS["reset"]

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def draw_track(pos1, pos2, name1, name2, prog1, prog2):
    """Render frame balapan ke terminal."""
    lines = []

    header = clr("=" * 62, "bold", "white")
    lines.append(header)
    lines.append(clr("  🏁  BALAPAN TERMINAL : MBG CARRY  vs  MOBIL F1  🏁", "bold", "yellow"))
    lines.append(header)
    lines.append("")

    # Lintasan & mobil
    for idx, (pos, car_fn, name, prog, col) in enumerate([
        (pos1, car_carry, name1, prog1, "yellow"),
        (pos2, car_f1,   name2, prog2, "cyan"),
    ]):
        car = car_fn(name)
        car_w = max(len(l) for l in car)

        # Hitung posisi render (clamp)
        render_pos = min(pos, FINISH_LINE)
        pad_left   = max(0, render_pos)

        # Garis lintasan atas / bawah
        track_top = clr("┌" + "─" * TRACK_WIDTH + "┐", "gray")
        track_bot = clr("└" + "─" * TRACK_WIDTH + "┘", "gray")

        # Progress bar di dalam lintasan
        filled = int((prog / 100) * TRACK_WIDTH)
        bar_inner = clr("█" * filled, col) + clr("░" * (TRACK_WIDTH - filled), "gray")
        track_prog = clr("│", "gray") + bar_inner + clr("│", "gray") + \
                     clr(f" {prog:3.0f}%", "bold", col)

        lines.append(track_top)
        lines.append(track_prog)

        # Baris mobil
        for row, car_line in enumerate(car):
            space_l = " " * pad_left
            # Potong jika melebihi lintasan
            available = TRACK_WIDTH - pad_left
            display   = car_line[:available]
            # Padding kanan
            pad_r     = " " * max(0, TRACK_WIDTH - pad_left - len(display))
            inner     = space_l + clr(display, col) + pad_r
            lines.append(clr("│", "gray") + inner + clr("│", "gray"))

        lines.append(track_bot)
        lines.append("")

    # Garis finish
    finish_marker = " " * 2 + clr(
        " " * (FINISH_LINE + 1) + "🏁 FINISH", "bold", "white"
    )
    lines.append(finish_marker)
    lines.append("")

    return "\n".join(lines)

# ─── Animasi intro ─────────────────────────────────────────────────────────────
def countdown():
    clear()
    msgs = [
        clr("\n\n        SIAP...\n", "bold", "yellow"),
        clr("\n\n        3...\n",    "bold", "white"),
        clr("\n\n        2...\n",    "bold", "yellow"),
        clr("\n\n        1...\n",    "bold", "cyan"),
        clr("\n\n        START! 🚦\n", "bold", "green"),
    ]
    for m in msgs:
        clear()
        print(m)
        time.sleep(0.7)

# ─── Main Game ─────────────────────────────────────────────────────────────────
def race():
    countdown()

    pos1, pos2 = 0, 0
    prog1, prog2 = 0.0, 0.0
    winner = None

    # Tentukan pemenang secara random di awal (tapi tetap tampil animasi)
    # Kita beri sedikit "boost tersembunyi" pada pemenang terpilih
    predetermined = random.choice([1, 2])

    lap   = 1
    frame = 0

    while winner is None:
        frame += 1

        # Hitung langkah masing-masing
        # Kecepatan sama, noise acak, tapi pemenang predetermined dapat +0.2 bias kecil
        step1 = BASE_SPEED + random.randint(0, MAX_NOISE)
        step2 = BASE_SPEED + random.randint(0, MAX_NOISE)

        # Bias kecil tersembunyi agar ada pemenang pasti tapi tetap terlihat seru
        if predetermined == 1:
            step1 += 0.3
        else:
            step2 += 0.3

        pos1 = min(pos1 + step1, FINISH_LINE + 5)
        pos2 = min(pos2 + step2, FINISH_LINE + 5)

        prog1 = min((pos1 / (FINISH_LINE + 1)) * 100, 100)
        prog2 = min((pos2 / (FINISH_LINE + 1)) * 100, 100)

        # Cek finish
        if pos1 >= FINISH_LINE and pos2 >= FINISH_LINE:
            winner = 0  # seri
        elif pos1 >= FINISH_LINE:
            winner = 1
        elif pos2 >= FINISH_LINE:
            winner = 2

        clear()
        print(draw_track(
            int(pos1), int(pos2),
            "MBG CARRY", "MOB F1 ",
            prog1, prog2
        ))

        # Lap counter (simulasi 3 lap)
        lap_progress = max(prog1, prog2)
        lap_show = int(lap_progress / 33.3) + 1
        print(clr(f"  Lap  {min(lap_show,3)} / 3", "bold", "white") +
              clr("   |   Frame: " + str(frame), "gray"))

        time.sleep(FRAME_DELAY)

    # ── Layar Hasil ──────────────────────────────────────────────────────────
    time.sleep(0.3)
    clear()
    print("\n" + clr("=" * 62, "bold", "white"))

    if winner == 1:
        print(clr("  🏆  PEMENANG :  MBG CARRY (SUZUKI)  🏆", "bold", "yellow"))
        trophy = r"""
         ___________
        '._==_==_=_.'
        .-\:      /-.
       | (|:.     |) |
        '-|:.     |-'
          \::.    /
           '::. .'
             ) (
           _.' '._
          `"""""""`
        """
        print(clr(trophy, "yellow"))
    elif winner == 2:
        print(clr("  🏆  PEMENANG :  MOBIL F1  🏆", "bold", "cyan"))
        trophy = r"""
         ___________
        '._==_==_=_.'
        .-\:      /-.
       | (|:.     |) |
        '-|:.     |-'
          \::.    /
           '::. .'
             ) (
           _.' '._
          `"""""""`
        """
        print(clr(trophy, "cyan"))
    else:
        print(clr("  🤝  SERI!  Dua mobil finish bersamaan!  🤝", "bold", "green"))

    print(clr("=" * 62, "bold", "white"))

    # Tampilkan ASCII art kedua mobil di akhir (mirip referensi)
    print("")
    print(clr("  Hasil Akhir:", "bold", "white"))
    print("")

    for line in car_carry("MBG CARRY"):
        print(clr("    " + line, "yellow"))
    print(clr(f"    Progress: {prog1:.1f}%", "yellow"))
    print("")
    for line in car_f1("MOB F1"):
        print(clr("    " + line, "cyan"))
    print(clr(f"    Progress: {prog2:.1f}%", "cyan"))

    print("")
    print(clr("  Tekan ENTER untuk main lagi, atau Ctrl+C untuk keluar.", "gray"))
    print("")

    try:
        input()
    except KeyboardInterrupt:
        print(clr("\n  Sampai jumpa! 👋\n", "bold", "white"))
        sys.exit(0)

# ─── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        race()
    except KeyboardInterrupt:
        print(clr("\n\n  Keluar dari game. Sampai jumpa! 👋\n", "bold", "white"))
        sys.exit(0)