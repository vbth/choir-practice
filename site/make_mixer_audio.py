#!/usr/bin/env python3
"""Stems for the mixer on the website (section "Üben" / "Practice"): docs/audio/mix/<percent>/<stem>.mp3 (website only, the skill is not touched)

  python3 site/make_mixer_audio.py [--lang en] [--out docs/audio/mix] [--soundfont NAME]

Renders the example piece with the skill's own functions (scripts/make_audio.py, imported, not changed) as separate mono stems
for each tempo step (TEMPI, in % of the written tempo): one choir stem per voice (s, a, t, b), one piano stem with all four
voices (acc) and the starting notes (intro). All stems of one step start at the same moment and have the same tempo, so the
browser can play them together and set each level.
No room reverb and no pan in the files: the page adds both live (Web Audio), so the stems stay small.
The gain is taken from the written tempo (100 %), so that the default mix sits at the loudness of the other recordings
(LUFS in make_audio.py); the other steps get the same gain, so the level does not jump when the tempo changes.
Needs fluidsynth, ffmpeg and the skill's Python packages (see scripts/setup.sh)."""
import argparse, json, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); SCR = os.path.join(HERE, '..', 'choir-practice', 'scripts')
sys.path.insert(0, SCR)
import make_audio as ma
import mido

LEVEL = {'voice': -3, 'acc': -9, 'intro': -3}   # dB of the default mix; the page starts with these levels at 100 %
TEMPI = [60, 75, 90, 100]                      # tempo steps in % of the written tempo

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
    tempo = spec['tempo']; base_tq = tempo['bpm'] * ma.BEATQ[tempo.get('beat') or 'quarter']
    order = [v.lower() for v in vids] + ['acc', 'intro']
    def level_of(name): return LEVEL['acc'] if name == 'acc' else LEVEL['intro'] if name == 'intro' else LEVEL['voice']

    with tempfile.TemporaryDirectory() as w:
        xml = os.path.join(w, 'score.musicxml')
        sh(sys.executable, os.path.join(SCR, 'build_score.py'), os.path.join(HERE, 'example', f'score.{A.lang}.json'), xml, '--workdir', w)

        def stems(pct):
            tq = base_tq * pct / 100
            score = ma.read_score(xml, ma.playback_order(spec), tq)
            for p in score['parts']: ma.velocities(p)
            ma.apply_fermatas(score); ma.to_ticks(score)
            clicks, start = ma.countin(score)
            # starting note = the voice's EARLIEST note in time
            first = {v: min(score['parts'][idx[v]]['tev'], key=lambda e: e[0])[2] for v in vids}
            tutti_keys = sorted(set(first.values()))
            delay = (len(tutti_keys) - 1) * (ma.INTRO['note_s'] + ma.INTRO['note_gap_s'])   # the voice stems wait for the tutti intro
            d = os.path.join(w, f'p{pct}'); os.makedirs(d)

            def stem(name, tracks, intro=None, shift=0.0):
                m = os.path.join(d, name + '.mid'); wav = os.path.join(d, name + '.wav')
                ma.write_midi(m, score, tracks, tq, [], start, intro=intro)
                mm = mido.MidiFile(m)                      # the own intro notes (channels 14, 15) are only wanted in the intro stem
                if intro is None or not intro[0]:
                    for tr in mm.tracks:
                        for j, msg in enumerate(tr):
                            if msg.type in ('note_on', 'note_off') and msg.channel in (14, 15): tr[j] = msg.copy(velocity=0)
                mm.save(m); ma.render(m, wav, mono=True)
                if shift > 0:
                    dl = os.path.join(d, name + '_d.wav')
                    sh('ffmpeg', '-y', '-loglevel', 'error', '-i', wav, '-af', f'adelay={round(shift * 1000)}', dl); wav = dl
                return wav

            wavs = {}
            for v in vids:
                wavs[v.lower()] = stem('v_' + v, [(idx[v], 127, 64, ma.PROG['choir'])], intro=([], ma.PROG['choir']), shift=delay)
            wavs['acc'] = stem('acc', [(idx[v], 127, 64, ma.PROG['piano']) for v in vids], intro=([], ma.PROG['piano']), shift=delay)
            wavs['intro'] = stem('intro', [], intro=(tutti_keys, ma.PROG['piano']))
            return wavs

        def ref_mix(wavs, out):
            cmd = ['ffmpeg', '-y', '-loglevel', 'error']
            for k in order: cmd += ['-i', wavs[k]]
            fc = ''.join(f'[{i}:a]volume={10 ** (level_of(k) / 20):.4f}[s{i}];' for i, k in enumerate(order))
            fc += ''.join(f'[s{i}]' for i in range(len(order))) + f'amix=inputs={len(order)}:normalize=0:duration=longest[o]'
            sh(*cmd, '-filter_complex', fc, '-map', '[o]', out); return out

        wav100 = stems(100)
        gain = ma.LUFS - lufs(ref_mix(wav100, os.path.join(w, 'ref100.wav')))
        print(f'default mix (100 %): gain {gain:+.1f} dB')
        for pct in TEMPI:
            wavs = wav100 if pct == 100 else stems(pct)
            od = os.path.join(A.out, str(pct)); os.makedirs(od, exist_ok=True)
            for k in order:
                sh('ffmpeg', '-y', '-loglevel', 'error', '-i', wavs[k], '-af', f'volume={gain + level_of(k):.2f}dB', '-ac', '1', '-ar', '44100',
                   '-b:a', '64k', '-map_metadata', '-1', os.path.join(od, k + '.mp3'))
            print(f'{pct} %: {len(order)} stems')
    tot = 0
    for root, _, files in os.walk(A.out):
        for f in sorted(files):
            tot += os.path.getsize(os.path.join(root, f))
    print('total', tot // 1024, 'kB')

if __name__ == '__main__':
    main()
