#!/usr/bin/env bash
# Checks and installs every tool the skill needs (idempotent). Prefers the MuseScore General soundfont (the sound bank only, not the program).
#   setup.sh --check    installs nothing; reports what is present, missing or different from the tested Python versions
#   setup.sh --stable   installs missing tools; Python packages in the tested versions of requirements-stable.txt (default)
#   setup.sh --latest   installs missing tools; Python packages in their newest versions (not tested)
#   add --verbose      prints every step (for the first run in a chat, so the steps can be shown to the user)
# Repairs itself: an interrupted dpkg run is finished first, a failed apt install is retried after an apt update.
# No `set -e`: a failed install must still reach the report at the end, which names what is missing.
MODE="--stable"; VERBOSE=0
for a in "$@"; do case "$a" in --verbose) VERBOSE=1;; --check|--stable|--latest) MODE="$a";; *) echo "usage: setup.sh [--check | --stable | --latest] [--verbose]"; exit 2;; esac; done
say() { [ "$VERBOSE" = 1 ] && echo "[setup] $*"; return 0; }
HERE="$(cd "$(dirname "$0")" && pwd)"; REQ="${CHOIR_PRACTICE_REQ:-$HERE/requirements-stable.txt}"   # CHOIR_PRACTICE_REQ: other pin file, for tests
SUDO=""; [ "$(id -u)" != "0" ] && command -v sudo >/dev/null && SUDO="sudo"

pyreport() {   # one row per Python package: tested vs installed version, then the overall state and a compact version line
python3 - "$REQ" <<'PY'
import sys
from importlib import metadata
rows, state, ver = [], 'ok', []
for line in open(sys.argv[1], encoding='utf-8'):
    line = line.split('#')[0].strip()
    if not line: continue
    name, _, tested = line.partition('==')
    try: have = metadata.version(name)
    except metadata.PackageNotFoundError: have = None
    st = 'ok' if have == tested else ('MISSING' if have is None else 'DIFFERS')
    if st == 'MISSING': state = 'missing'
    elif st == 'DIFFERS' and state != 'missing': state = 'differs'
    rows.append(f'python {name:<10} tested {tested:<8} installed {have or "-":<8} {st}')
    ver.append(f'{name} {have or "-"}')
print('\n'.join(rows)); print('python state:', state); print('versions:', ', '.join(ver))
PY
}

need_list() {   # apt packages that are missing; GeneralUser GS is bundled, so a missing MuseScore soundfont is not an error
  need=()
  command -v fluidsynth >/dev/null || need+=(fluidsynth)
  command -v ffmpeg >/dev/null || need+=(ffmpeg)
  command -v pdftoppm >/dev/null || need+=(poppler-utils)
  [ -f /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf ] || need+=(fonts-dejavu-core)
  [ -f /usr/share/sounds/sf3/MuseScore_General_Full.sf3 ] || need+=(musescore-general-soundfont)
}
install_apt() {   # one install; on failure: finish an interrupted dpkg run, update the package lists, retry; returns 0 when done
  local log; log=$(mktemp)
  $SUDO dpkg --configure -a >>"$log" 2>&1
  say "apt install $*"
  $SUDO apt-get install -y -q "$@" >>"$log" 2>&1 && { say "apt ok"; rm -f "$log"; return 0; }
  say "apt install failed, updating the package lists and retrying"
  $SUDO apt-get update -q >>"$log" 2>&1
  $SUDO apt-get install -y -q "$@" >>"$log" 2>&1 && { say "apt ok after the retry"; rm -f "$log"; return 0; }
  echo "apt install failed (no apt, no rights or no network) – last lines of the log:"; tail -n 6 "$log"; rm -f "$log"; return 1
}
need_list

if [ "$MODE" = "--check" ]; then
  [ ${#need[@]} -gt 0 ] && echo "apt would install: ${need[*]}" || echo "apt: nothing to install"
  pyreport
else
  for round in 1 2; do   # a second round repairs what the first one could not install
    [ ${#need[@]} -eq 0 ] && break
    say "round $round: apt packages missing: ${need[*]}"
    install_apt "${need[@]}"; need_list
  done
  [ ${#need[@]} -eq 0 ] || echo "still missing after the repair: ${need[*]}"
  for round in 1 2; do   # Python packages: the second round repeats the install without the cache
    say "round $round: pip install (${MODE#--})"
    if [ "$MODE" = "--stable" ]; then
      pip install -q --break-system-packages -r "$REQ" 2>/dev/null || pip install -q -r "$REQ" 2>/dev/null || pip install -q --no-cache-dir -r "$REQ" 2>/dev/null
    else
      PK=$(sed 's/#.*//; s/==.*//' "$REQ" | tr '\n' ' ')
      pip install -q -U --break-system-packages $PK 2>/dev/null || pip install -q -U $PK 2>/dev/null
    fi
    python3 -c "import verovio,cairosvg,lxml,pypdf,mido,reportlab,PIL,numpy,scipy" 2>/dev/null && break
  done
  python3 -c "import verovio,cairosvg,lxml,pypdf,mido,reportlab,PIL,numpy,scipy" 2>/dev/null || echo "pip install FAILED for: run setup.sh --check for the list"
  python3 -c "import verovio,cairosvg,lxml,pypdf,mido,reportlab,PIL,numpy,scipy; print('python ok')" 2>/dev/null || echo "python MISSING: run setup.sh --check for the list"
  echo "mode: ${MODE#--} $([ "$MODE" = "--stable" ] && echo '(tested versions)' || echo '(newest versions, not tested)')"
  pyreport
fi
for c in fluidsynth ffmpeg pdftoppm; do command -v $c >/dev/null && echo "$c ok" || echo "$c MISSING"; done
python3 "$HERE/check_third_party.py" --brief 2>&1 | tail -3   # third-party rights: every installed component must be named in THIRD_PARTY_NOTICES.md
([ -f /usr/share/sounds/sf3/MuseScore_General_Full.sf3 ] && echo "soundfont ok (MuseScore General Full)") || ([ -f "$(dirname "$HERE")/assets/soundfonts/GeneralUser-GS.sf3" ] && echo "soundfont fallback GeneralUser GS (bundled in the skill, report this)") || ([ -f /usr/share/sounds/sf2/FluidR3_GM.sf2 ] && echo "soundfont fallback FluidR3_GM (lower quality – report this)") || echo "soundfont MISSING"
