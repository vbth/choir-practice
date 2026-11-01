#!/usr/bin/env python3
"""Stems for the mixer on the website (section "Üben" / "Practice"): docs/audio/mix/<id>.mp3  (website only, the skill is not touched)

  python3 site/make_mixer_audio.py [--lang en] [--out docs/audio/mix] [--soundfont NAME]

Renders the example piece with the skill's own functions (scripts/make_audio.py, imported, not changed) as separate mono stems:
one choir stem per voice (s, a, t, b), one piano stem with all four voices (acc) and the starting notes (intro).
All stems start at the same moment and have the same tempo, so the browser can play them together and set each level.
No room reverb and no pan in the files: the page adds both live (Web Audio), so the stems stay small.
The gain is chosen so that the default mix (all voices -3 dB, piano -9 dB) sits at the loudness of the other recordings (LUFS in make_audio.py).
Needs fluidsynth, ffmpeg and the skill's Python packages (see scripts/setup.sh)."""
import argparse, json, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); SCR = os.path.join(HERE, '..', 'choir-practice', 'scripts')
sys.path.insert(0, SCR)
import make_audio as ma
import mido

LEVEL = {'voice': -3, 'acc': -9}          # dB of the default mix; the page starts with these levels at 100 %

def sh(*a): subprocess.run(a, check=True, capture_output=True)

# Integrated loudness (LUFS) of a wav file
def lufs(wav):
    r = subprocess.run(['ffmpeg', '-nostats', '-i', wav, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True)
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r.stderr)[-1])

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--lang', default='en'); ap.add_argument('--out', default=os.path.join(HERE, '..', 'docs', 'audio', 'mix'))
    ap.add_argument('--soundfont', default='generaluser')
    A = ap.parse_args()
    sf = ma.SF_CHOICES.get(A.soundfont, [A.soundfont]); ma.SF = next((p for p in sf if os.path.exists(p)), None) or sys.exit('soundfont not found')
    os.makedirs(A.out, exist_ok=True)
    spec = json.load(open(os.path.join(HERE, 'example', f'score.{A.lang}.json'), encoding='utf-8'))
    vids = [v['id'] for v in spec['voices']]; idx = {v: k for k, v in enumerate(vids)}
    tempo = spec['tempo']; tq = tempo['bpm'] * ma.BEATQ[tempo.get('beat') or 'quarter']
    with tempfile.TemporaryDirectory() as w:
        xml = os.path.join(w, 'score.musicxml')
        sh(sys.executable, os.path.join(SCR, 'build_score.py'), os.path.join(HERE, 'example', f'score.{A.lang}.json'), xml, '--workdir', w)
        score = ma.read_score(xml, ma.playback_order(spec), tq)
        for p in score['parts']: ma.velocities(p)
        ma.apply_fermatas(score); ma.to_ticks(score)
        clicks, start = ma.countin(score)
        first = {v: min(score['parts'][idx[v]]['tev'], key=lambda e: e[0])[2] for v in vids}
        tutti_keys = sorted(set(first.values()))
        delay = (len(tutti_keys) - 1) * (ma.INTRO['note_s'] + ma.INTRO['note_gap_s'])   # same shift as the tutti file: the voice stems wait for the starting notes

        def stem(name, tracks, intro=None, shift=0.0):
            m = os.path.join(w, name + '.mid'); wav = os.path.join(w, name + '.wav')
            ma.write_midi(m, score, tracks, tq, [], start, intro=intro)
            mm = mido.MidiFile(m)                      # the own intro notes (channels 14, 15) are only wanted in the intro stem
            if intro is None or not intro[0]:
                for tr in mm.tracks:
                    for j, msg in enumerate(tr):
                        if msg.type in ('note_on', 'note_off') and msg.channel in (14, 15): tr[j] = msg.copy(velocity=0)
            mm.save(m); ma.render(m, wav, mono=True)
            if shift > 0:
                d = os.path.join(w, name + '_d.wav'); ms = round(shift * 1000)
                sh('ffmpeg', '-y', '-loglevel', 'error', '-i', wav, '-af', f'adelay={ms}', d); wav = d
            return wav

        wavs = {}
        for v in vids:
            # tracks: (part index, loudness 0..127, pan 0..127, GM program); centre pan, the page pans
            wavs[v.lower()] = stem('v_' + v, [(idx[v], 127, 64, ma.PROG['choir'])], intro=([], ma.PROG['choir']), shift=delay)
        wavs['acc'] = stem('acc', [(idx[v], 127, 64, ma.PROG['piano']) for v in vids], intro=([], ma.PROG['piano']), shift=delay)
        wavs['intro'] = stem('intro', [], intro=(tutti_keys, ma.PROG['piano']))
        # gain: loudness of the default mix (all voices + piano, 100 %) -> target
        def g(db): return 10 ** (db / 20)
        ins = [(wavs[v.lower()], LEVEL['voice']) for v in vids] + [(wavs['acc'], LEVEL['acc']), (wavs['intro'], -3)]
        cmd = ['ffmpeg', '-y', '-loglevel', 'error']
        for f, _ in ins: cmd += ['-i', f]
        fc = ''.join(f'[{k}:a]volume={g(db):.4f}[s{k}];' for k, (_, db) in enumerate(ins)) + ''.join(f'[s{k}]' for k in range(len(ins))) + f'amix=inputs={len(ins)}:normalize=0:duration=longest[o]'
        ref = os.path.join(w, 'ref.wav'); sh(*cmd, '-filter_complex', fc, '-map', '[o]', ref)
        gain = ma.LUFS - lufs(ref); print(f'default mix {lufs(ref):.1f} LUFS -> gain {gain:+.1f} dB')
        for name, wav in wavs.items():
            db = gain + (LEVEL['voice'] if name in [v.lower() for v in vids] else LEVEL['acc'] if name == 'acc' else -3)
            sh('ffmpeg', '-y', '-loglevel', 'error', '-i', wav, '-af', f'volume={db:.2f}dB', '-ac', '1', '-ar', '44100', '-b:a', '64k', '-map_metadata', '-1', os.path.join(A.out, name + '.mp3'))
    tot = 0
    for f in sorted(os.listdir(A.out)):
        n = os.path.getsize(os.path.join(A.out, f)); tot += n; print(f, n // 1024, 'kB')
    print('total', tot // 1024, 'kB')

if __name__ == '__main__':
    main()
