#!/usr/bin/env bash
# Checks and installs every tool the skill needs (idempotent). Prefers the MuseScore General soundfont (the sound bank only, not the program).
#   setup.sh --check    installs nothing; reports what is present, missing or different from the tested Python versions
#   setup.sh --stable   installs missing tools; Python packages in the tested versions of requirements-stable.txt (default)
#   setup.sh --latest   installs missing tools; Python packages in their newest versions (not tested)
# No `set -e`: a failed install must still reach the report at the end, which names what is missing.
MODE="${1:---stable}"
case "$MODE" in --check|--stable|--latest) ;; *) echo "usage: setup.sh --check | --stable | --latest"; exit 2;; esac
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

need=()
command -v fluidsynth >/dev/null || need+=(fluidsynth)
[ -f /usr/share/sounds/sf2/FluidR3_GM.sf2 ] || need+=(fluid-soundfont-gm)
command -v ffmpeg >/dev/null || need+=(ffmpeg)
command -v pdftoppm >/dev/null || need+=(poppler-utils)
[ -f /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf ] || need+=(fonts-dejavu-core)
PLEX=/usr/share/fonts/truetype/ibm-plex/IBMPlexSans-Regular.ttf; PLEX_USER="$HOME/.fonts/ibm-plex/IBMPlexSans-Regular.ttf"
[ -f "$PLEX" ] || [ -f "$PLEX_USER" ] || need+=(fonts-ibm-plex)
[ -f /usr/share/sounds/sf3/MuseScore_General_Full.sf3 ] || need+=(musescore-general-soundfont)

if [ "$MODE" = "--check" ]; then
  [ ${#need[@]} -gt 0 ] && echo "apt would install: ${need[*]}" || echo "apt: nothing to install"
  pyreport
else
  if [ ${#need[@]} -gt 0 ]; then
    echo "apt: ${need[*]}"
    ($SUDO apt-get install -y -q "${need[@]}" >/dev/null 2>&1) || ($SUDO apt-get update -q >/dev/null 2>&1 && $SUDO apt-get install -y -q "${need[@]}" >/dev/null 2>&1) || \
      echo "apt install failed (no apt, no rights or no network) – see the report below"
  fi
  if [ ! -f "$PLEX" ] && [ ! -f "$PLEX_USER" ]; then   # no apt: the fonts zip that every release carries (no fonts in git)
    FZ="$(mktemp -d)/fonts.zip"
    (curl -fsSL -o "$FZ" https://github.com/vbth/choir-practice/releases/latest/download/choir-practice-fonts.zip && mkdir -p "$HOME/.fonts/ibm-plex" && python3 -c "import sys,zipfile; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" "$FZ" "$HOME/.fonts/ibm-plex" && fc-cache -f >/dev/null 2>&1) || \
      echo "IBM Plex Sans could not be installed (apt package fonts-ibm-plex or the fonts zip of the release) – see the report below"
  fi
  if [ "$MODE" = "--stable" ]; then
    pip install -q --break-system-packages -r "$REQ" 2>/dev/null || pip install -q -r "$REQ" || \
      echo "pip install of the tested versions FAILED (for example no ready-made package for this Python) – see the report below"
  else
    PK=$(sed 's/#.*//; s/==.*//' "$REQ" | tr '\n' ' ')
    pip install -q -U --break-system-packages $PK 2>/dev/null || pip install -q -U $PK || echo "pip install of the newest versions FAILED – see the report below"
  fi
  python3 -c "import verovio,cairosvg,lxml,pypdf,mido,reportlab,PIL,numpy,scipy,pydantic; print('python ok')" 2>/dev/null || echo "python MISSING: run setup.sh --check for the list"
  echo "mode: ${MODE#--} $([ "$MODE" = "--stable" ] && echo '(tested versions)' || echo '(newest versions, not tested)')"
  pyreport
fi
([ -f "$PLEX" ] || [ -f "$PLEX_USER" ]) && echo "fonts ok (IBM Plex Sans)" || echo "fonts MISSING (IBM Plex Sans: the PDFs cannot be built)"
for c in fluidsynth ffmpeg pdftoppm; do command -v $c >/dev/null && echo "$c ok" || echo "$c MISSING"; done
python3 "$HERE/check_third_party.py" --brief 2>&1 | tail -3   # third-party rights: every installed component must be named in THIRD_PARTY_NOTICES.md
([ -f /usr/share/sounds/sf3/MuseScore_General_Full.sf3 ] && echo "soundfont ok (MuseScore General Full)") || ([ -f /usr/share/sounds/sf2/FluidR3_GM.sf2 ] && echo "soundfont fallback FluidR3_GM (lower quality – report this)") || echo "soundfont MISSING"
