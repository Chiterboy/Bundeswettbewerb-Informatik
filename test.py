from pathlib import Path
from collections import defaultdict

# ---------- 1. Einlesen ----------

def read_grid(path: Path):
    lines = path.read_text().strip().splitlines()
    assert len(lines) == 4
    grid = [list(line) for line in lines]
    assert all(len(row) == 4 for row in grid)
    return grid

def read_wordlist(path: Path):
    words = [line.strip().upper() for line in path.read_text().splitlines() if line.strip()]
    return words

# ---------- 2. Wortplätze bestimmen ----------

def find_slots(grid):
    slots = []  # jedes Slot: dict mit info
    R, C = 4, 4

    # horizontal
    for r in range(R):
        c = 0
        while c < C:
            if grid[r][c] == "#":
                c += 1
                continue
            start = c
            while c < C and grid[r][c] != "#":
                c += 1
            length = c - start
            if length >= 2:
                cells = [(r, start + i) for i in range(length)]
                slots.append({
                    "start": (r, start),
                    "dir": "H",
                    "length": length,
                    "cells": cells,
                })
    # vertikal
    for c in range(C):
        r = 0
        while r < R:
            if grid[r][c] == "#":
                r += 1
                continue
            start = r
            while r < R and grid[r][c] != "#":
                r += 1
            length = r - start
            if length >= 2:
                cells = [(start + i, c) for i in range(length)]
                slots.append({
                    "start": (start, c),
                    "dir": "V",
                    "length": length,
                    "cells": cells,
                })
    return slots

# ---------- 3. Wörter nach Länge gruppieren ----------

def group_words_by_len(words):
    d = defaultdict(list)
    for w in words:
        d[len(w)].append(w)
    return d

# ---------- 4. Backtracking ----------

def get_fixed_letters_in_slot(grid, slot):
    # liefert dict: position_in_slot (0..len-1) -> Buchstabe, falls im Grid schon gesetzt (nicht '.')
    fixed = {}
    for i, (r, c) in enumerate(slot["cells"]):
        ch = grid[r][c]
        if ch not in (".", "#"):
            fixed[i] = ch
    return fixed

def candidates_for_slot(grid, slot, words_by_len):
    L = slot["length"]
    candidates = []
    fixed = get_fixed_letters_in_slot(grid, slot)
    for w in words_by_len.get(L, []):
        ok = True
        for i, ch in fixed.items():
            if w[i] != ch:
                ok = False
                break
        # zusätzlich: prüfen, ob an Kreuzungen bereits Buchstaben gesetzt sind, die nicht passen
        if ok:
            for i, (r, c) in enumerate(slot["cells"]):
                gch = grid[r][c]
                if gch not in (".", "#") and gch != w[i]:
                    ok = False
                    break
        if ok:
            candidates.append(w)
    return candidates

def place_word(grid, slot, word):
    for i, (r, c) in enumerate(slot["cells"]):
        grid[r][c] = word[i]

def remove_word(grid, slot, length):
    for i, (r, c) in enumerate(slot["cells"]):
        # nur zurücksetzen, wenn nicht ursprünglich fest vorgegeben
        # hier vereinfacht: wir merken uns das nicht; im echten Code besser tracken.
        grid[r][c] = "."

def solve(grid, slots, words_by_len, idx=0):
    if idx == len(slots):
        return True  # alle Slots belegt, Lösung gefunden

    slot = slots[idx]

    # Kandidaten ermitteln
    cands = candidates_for_slot(grid, slot, words_by_len)
    # Heuristik: nach „wenig Kandidaten zuerst” sortieren wir die Slots vorher; hier einfach so
    for w in cands:
        # vorläufig setzen
        old = [grid[r][c] for (r, c) in slot["cells"]]
        place_word(grid, slot, w)
        if solve(grid, slots, words_by_len, idx + 1):
            return True
        # backtrack
        for i, (r, c) in enumerate(slot["cells"]):
            grid[r][c] = old[i]
    return False

# ---------- 5. Hauptprogramm ----------

def main():
    # Pfade anpassen
    grid_path = Path("kreuz01.txt")      # Beispiel‑Eingabedatei vom BWINF
    wordlist_path = Path("wortliste.txt")  # Wortliste aus dem Material

    grid = read_grid(grid_path)
    words = read_wordlist(wordlist_path)
    words_by_len = group_words_by_len(words)

    slots = find_slots(grid)

    # Heuristik: Slots mit weniger Kandidaten zuerst
    # grob: nach Länge und Anzahl fester Buchstaben sortieren
    def slot_key(slot):
        fixed_count = sum(
            1 for (r, c) in slot["cells"]
            if grid[r][c] not in (".", "#")
        )
        # weniger Kandidaten ≈ kürzere Länge + mehr feste Buchstaben
        return (slot["length"], -fixed_count)

    slots.sort(key=slot_key)

    if solve(grid, slots, words_by_len):
        print("Lösung gefunden:")
        for row in grid:
            print("".join(row))
    else:
        print("Keine Lösung mit dieser Wortliste / diesem Grid.")

if __name__ == "__main__":
    main()