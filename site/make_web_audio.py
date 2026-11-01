#!/usr/bin/env python3
"""Web recordings for the website (section "Üben" / "Practice"): docs/audio/<voice>_<stage>_<sound>[_slow].mp3

  python3 site/make_web_audio.py PACK_ZIP [--out docs/audio]
  python3 site/make_web_audio.py --cover-only [--out docs/audio]

PACK_ZIP is an example package of the release (the English one: the audio of both languages is identical, so one set serves both pages).
Takes the voice ZIPs inside it, converts 42 recordings to MP3 (80 kbit/s, no tags, only the album art docs/img/cover-en.jpg as a 300 px picture): per voice (s, a, t, b) x sound (choir, piano) x
alone / with accompaniment (normal and slow) / in the choir, plus tutti per sound. Needs ffmpeg.
--cover-only embeds the cover into the existing files without touching the audio (stream copy), e.g. after a new cover."""
import glob, os, shutil, subprocess, sys, tempfile, zipfile
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
STAGES = {'solo': {'': '2', '_slow': '1'}, 'accomp': {'': '4', '_slow': '3'}, 'choir': {'': '5'}}   # number of the file in the voice ZIP
SOUNDS = {'choir': '3', 'piano': '4'}                                                                 # folder number in the voice ZIP

# Album art for the web files: the cover of the English example (the audio serves both languages), scaled down to keep the files small
def small_cover(dst):
    Image.open(os.path.join(HERE, '..', 'docs', 'img', 'cover-en.jpg')).convert('RGB').resize((300, 300), Image.Resampling.LANCZOS).save(dst, 'JPEG', quality=85, subsampling=0, optimize=True)

COVER_MAP = ['-map', '1:v', '-c:v', 'copy', '-disposition:v', 'attached_pic', '-id3v2_version', '3', '-metadata:s:v', 'title=Cover', '-metadata:s:v', 'comment=Cover (front)']

# Converts the voice recordings from an example ZIP into the small MP3s the website player streams
def main():
    out = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else os.path.join(HERE, '..', 'docs', 'audio')
    os.makedirs(out, exist_ok=True)
    with tempfile.TemporaryDirectory() as w:
        cover = os.path.join(w, 'cover.jpg'); small_cover(cover)
        if '--cover-only' in sys.argv:   # stream copy: the audio stays bit-identical, only the picture is added
            files = sorted(glob.glob(os.path.join(out, '*.mp3')))
            for f in files:
                tmp = os.path.join(w, 'tmp.mp3')
                subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', f, '-i', cover, '-map', '0:a', '-c:a', 'copy', '-map_metadata', '-1'] + COVER_MAP + [tmp], check=True)
                shutil.move(tmp, f)
            print(f'cover embedded in {len(files)} files in {os.path.relpath(out)}'); return
        zipfile.ZipFile(sys.argv[1]).extractall(w)
        for vz in glob.glob(os.path.join(w, '2_*', '*.zip')): zipfile.ZipFile(vz).extractall(os.path.join(w, 'v', os.path.basename(vz)[:-4]))
        jobs = []
        for snd, dn in SOUNDS.items():
            for v in 'SATB':
                for st, files in STAGES.items():
                    for suf, n in files.items():
                        src = glob.glob(os.path.join(w, 'v', f'{v}_*', f'{v}_*', f'{dn}_{v}_*', f'{n}_{v}_*.mp3')); assert len(src) == 1, (v, snd, st, n, src)
                        jobs.append((src[0], f'{v.lower()}_{st}_{snd}{suf}.mp3'))
            src = glob.glob(os.path.join(w, 'v', 'S_*', 'S_*', f'{dn}_S_*', '6_S_*.mp3')); assert len(src) == 1
            jobs.append((src[0], f'tutti_{snd}.mp3'))
        for s, o in jobs:
            subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', s, '-i', cover, '-map', '0:a', '-map_metadata', '-1', '-c:a', 'libmp3lame', '-b:a', '80k', '-ar', '44100'] + COVER_MAP + [os.path.join(out, o)], check=True)
    print(f'{len(jobs)} files in {os.path.relpath(out)}')

if __name__ == '__main__':
    main()
