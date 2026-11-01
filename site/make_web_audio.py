#!/usr/bin/env python3
"""Web recordings for the website (section "Üben" / "Practice"): docs/audio/<voice>_<stage>_<sound>[_slow].mp3

  python3 site/make_web_audio.py PACK_ZIP [--out docs/audio]

PACK_ZIP is an example package of the release (the English one: the audio of both languages is identical, so one set serves both pages).
Takes the voice ZIPs inside it, converts 42 recordings to MP3 (80 kbit/s, no cover, no tags): per voice (s, a, t, b) x sound (choir, piano) x
alone / with accompaniment (normal and slow) / in the choir, plus tutti per sound. Needs ffmpeg."""
import glob, os, subprocess, sys, tempfile, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
STAGES = {'solo': {'': '2', '_slow': '1'}, 'accomp': {'': '4', '_slow': '3'}, 'choir': {'': '5'}}   # number of the file in the voice ZIP
SOUNDS = {'choir': '3', 'piano': '4'}                                                                 # folder number in the voice ZIP

# Converts the voice recordings from an example ZIP into the small MP3s the website player streams
def main():
    zp = sys.argv[1]; out = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else os.path.join(HERE, '..', 'docs', 'audio')
    os.makedirs(out, exist_ok=True)
    with tempfile.TemporaryDirectory() as w:
        zipfile.ZipFile(zp).extractall(w)
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
            subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', s, '-vn', '-map_metadata', '-1', '-c:a', 'libmp3lame', '-b:a', '80k', '-ar', '44100', os.path.join(out, o)], check=True)
    print(f'{len(jobs)} files in {os.path.relpath(out)}')

if __name__ == '__main__':
    main()
