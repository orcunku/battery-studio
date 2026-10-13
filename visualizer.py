import base64
import json
from pathlib import Path

import streamlit.components.v1 as html_comp


def render_drum_visualizer(song_data):
    component_song_data = dict(song_data)
    audio_path = Path(song_data.get("audioUrl", ""))
    if audio_path.is_file():
        audio_data = base64.b64encode(audio_path.read_bytes()).decode("ascii")
        component_song_data["audioUrl"] = f"data:audio/mpeg;base64,{audio_data}"
    elif component_song_data.get("audioUrl", "").startswith(("assets/", "./assets/")):
        component_song_data["audioUrl"] = ""
    song_json = json.dumps(component_song_data)

    js_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/tone/14.8.49/Tone.js" onerror="window.visualizerLibraryLoadFailure = 'Tone.js';"></script>
        <style>
            :root {{ color-scheme: dark; font-family: 'Trebuchet MS', sans-serif; }}
            * {{ box-sizing: border-box; }}
            body {{ margin: 0; background: #111312; color: #f1f0e9; }}
            #studio {{ width: 100%; max-width: 1120px; margin: 0 auto; }}
            #stage {{ position: relative; width: 100%; aspect-ratio: 16 / 9; min-height: 340px; max-height: 660px; overflow: hidden; background: #111312; }}
            #stage canvas {{ display: block; width: 100%; height: 100%; }}
            #stage-status {{ position: absolute; inset: 0; display: grid; place-items: center; color: #d5d2c7; font-size: 14px; pointer-events: none; }}
            #coach-cue {{ display: grid; grid-template-columns: 1fr; gap: 4px; margin: 10px 4px 0; padding: 11px 14px; border-left: 3px solid #d5a53a; background: #20231f; color: #f1f0e9; }}
            #coach-eyebrow {{ display: block; color: #e6bd60; font-size: 10px; font-weight: 700; }}
            #coach-title {{ display: block; font-size: 14px; }}
            #coach-copy {{ margin: 0; color: #d2d0c7; font-size: 12px; line-height: 1.4; }}
            #controls {{ display: grid; grid-template-columns: auto auto minmax(90px, 1fr) auto; align-items: center; gap: 12px; padding: 12px 4px 6px; }}
            button {{ border: 1px solid #55594f; border-radius: 4px; color: #f2efe4; background: #282b27; padding: 9px 14px; min-height: 38px; font: 600 13px 'Trebuchet MS', sans-serif; cursor: pointer; }}
            button:hover:not(:disabled) {{ border-color: #d1a448; background: #34372f; }}
            button:disabled {{ opacity: .45; cursor: wait; }}
            #playBtn {{ background: #d5a53a; border-color: #d5a53a; color: #14140f; }}
            #playBtn:hover:not(:disabled) {{ background: #edbd4d; }}
            #timeScrubber {{ width: 100%; accent-color: #d5a53a; cursor: pointer; }}
            #time-display {{ min-width: 94px; color: #b8b7ae; font: 12px ui-monospace, monospace; text-align: right; }}
            #legend {{ display: flex; justify-content: center; flex-wrap: wrap; gap: 15px; padding: 3px 0 12px; color: #b8b7ae; font: 11px 'Trebuchet MS', sans-serif; }}
            .legend-item {{ display: inline-flex; align-items: center; gap: 6px; }}
            .legend-dot {{ width: 8px; height: 8px; border-radius: 50%; background: var(--dot); box-shadow: 0 0 8px var(--dot); }}
            @media (max-width: 560px) {{
                #stage {{ aspect-ratio: 4 / 3; min-height: 300px; }}
                #controls {{ grid-template-columns: auto auto 1fr; gap: 8px; }}
                #timeScrubber {{ grid-column: 1 / 3; grid-row: 2; }}
                #time-display {{ grid-column: 3; grid-row: 2; }}
                button {{ padding: 8px 10px; font-size: 12px; }}
                #legend {{ gap: 9px 12px; }}
                #coach-cue {{ margin: 8px 2px 0; padding: 9px 11px; }}
                #coach-copy {{ font-size: 11px; }}
            }}
        </style>
    </head>
    <body>
        <main id="studio">
            <div id="stage">
                <canvas id="stage-canvas" aria-label="2D drum kit visualizer"></canvas>
                <div id="stage-status">Loading drum stage...</div>
            </div>
            <aside id="coach-cue" aria-live="polite">
                <span id="coach-eyebrow">LIVE COACH</span>
                <strong id="coach-title">Ready when you are</strong>
                <p id="coach-copy">The coach will preview challenging fills and busy phrases.</p>
            </aside>
            <div id="controls">
                <button id="playBtn" disabled>Play Track</button>
                <button id="stopBtn">Stop</button>
                <input type="range" id="timeScrubber" min="0" max="100" value="0" step="0.05" aria-label="Seek through song">
                <span id="time-display">00:00 / 00:00</span>
            </div>
            <div id="legend" aria-label="Drum kit legend">
                <span class="legend-item"><i class="legend-dot" style="--dot:#4bc9dd"></i>Kick</span>
                <span class="legend-item"><i class="legend-dot" style="--dot:#ee667a"></i>Snare</span>
                <span class="legend-item"><i class="legend-dot" style="--dot:#e2bc56"></i>Hi-hat</span>
                <span class="legend-item"><i class="legend-dot" style="--dot:#71c28a"></i>Toms</span>
                <span class="legend-item"><i class="legend-dot" style="--dot:#e48c4e"></i>Cymbals</span>
            </div>
        </main>
        <script>
            const songData = {song_json};
            const stage = document.getElementById('stage');
            const status = document.getElementById('stage-status');
            const playButton = document.getElementById('playBtn');
            const scrubber = document.getElementById('timeScrubber');
            const timeDisplay = document.getElementById('time-display');
            const coachEyebrow = document.getElementById('coach-eyebrow');
            const coachTitle = document.getElementById('coach-title');
            const coachCopy = document.getElementById('coach-copy');
            if (!window.Tone) {{
                status.textContent = 'Tone.js could not load. Check your internet connection and reload.';
                throw new Error('Tone.js failed to load.');
            }}
            const canvas = document.getElementById('stage-canvas');
            const context = canvas.getContext('2d');
            if (!context) {{
                status.textContent = 'The 2D drum stage could not be initialized in this browser.';
                throw new Error('Canvas 2D context is unavailable.');
            }}
            const pixelRatio = Math.min(window.devicePixelRatio || 1, 1.5);
            let animationFrame = null;
            let previousFrame = performance.now();
            const partColors = {{
                kick: '#4bc9dd', snare: '#ee667a', hihat: '#e2bc56',
                tom1: '#71c28a', tom2: '#65aa7a', floorTom: '#72c29a',
                crash: '#e48c4e', ride: '#d6ad58'
            }};
            const parts = {{
                kick: {{ x: 500, y: 386, rx: 65, ry: 51, kind: 'drum', label: 'KICK', pulse: 0 }},
                snare: {{ x: 348, y: 301, rx: 43, ry: 36, kind: 'drum', label: 'SNARE', pulse: 0 }},
                tom1: {{ x: 440, y: 243, rx: 39, ry: 33, kind: 'drum', label: 'TOM 1', pulse: 0 }},
                tom2: {{ x: 550, y: 235, rx: 41, ry: 34, kind: 'drum', label: 'TOM 2', pulse: 0 }},
                floorTom: {{ x: 684, y: 306, rx: 49, ry: 41, kind: 'drum', label: 'FLOOR TOM', pulse: 0 }},
                hihat: {{ x: 245, y: 252, rx: 57, ry: 31, kind: 'cymbal', label: 'HI-HAT', pulse: 0 }},
                crash: {{ x: 340, y: 145, rx: 72, ry: 39, kind: 'cymbal', label: 'CRASH', pulse: 0 }},
                ride: {{ x: 729, y: 158, rx: 79, ry: 42, kind: 'cymbal', label: 'RIDE', pulse: 0 }}
            }};

            function drawStage() {{
                const width = stage.clientWidth;
                const height = stage.clientHeight;
                context.setTransform(pixelRatio * width / 1000, 0, 0, pixelRatio * height / 562, 0, 0);
                context.clearRect(0, 0, 1000, 562);

                const background = context.createLinearGradient(0, 0, 0, 562);
                background.addColorStop(0, '#191d1b');
                background.addColorStop(1, '#101211');
                context.fillStyle = background;
                context.fillRect(0, 0, 1000, 562);

                context.fillStyle = '#202321';
                context.beginPath();
                context.ellipse(500, 305, 435, 245, 0, 0, Math.PI * 2);
                context.fill();
                context.strokeStyle = 'rgba(230, 225, 205, 0.035)';
                context.lineWidth = 2;
                context.stroke();

                context.strokeStyle = '#59605c';
                context.lineWidth = 5;
                [['hihat', 'snare'], ['crash', 'tom1'], ['ride', 'floorTom']].forEach(([from, to]) => {{
                    context.beginPath();
                    context.moveTo(parts[from].x, parts[from].y + 14);
                    context.lineTo(parts[to].x, parts[to].y - 12);
                    context.stroke();
                }});

                Object.entries(parts).forEach(([key, part]) => {{
                    const color = partColors[key];
                    const pulse = part.pulse;
                    context.save();
                    context.translate(part.x, part.y);
                    context.shadowColor = color;
                    context.shadowBlur = 42 * pulse;
                    context.fillStyle = `rgba(${{parseInt(color.slice(1, 3), 16)}}, ${{parseInt(color.slice(3, 5), 16)}}, ${{parseInt(color.slice(5, 7), 16)}}, ${{0.2 * pulse}})`;
                    context.beginPath();
                    context.ellipse(0, 0, part.rx * 1.35, part.ry * 1.45, 0, 0, Math.PI * 2);
                    context.fill();
                    context.shadowBlur = 0;

                    if (part.kind === 'cymbal') {{
                        const cymbal = context.createRadialGradient(-part.rx * 0.2, -part.ry * 0.4, 2, 0, 0, part.rx);
                        cymbal.addColorStop(0, pulse ? '#f6d889' : '#d0a653');
                        cymbal.addColorStop(1, '#74572f');
                        context.fillStyle = cymbal;
                        context.beginPath();
                        context.ellipse(0, 0, part.rx, part.ry, 0, 0, Math.PI * 2);
                        context.fill();
                        context.strokeStyle = '#d8b86e';
                        context.lineWidth = 2;
                        context.stroke();
                        context.beginPath();
                        context.ellipse(0, 0, part.rx * 0.73, part.ry * 0.68, 0, 0, Math.PI * 2);
                        context.strokeStyle = 'rgba(53, 42, 25, 0.55)';
                        context.lineWidth = 1;
                        context.stroke();
                        context.fillStyle = '#e1c17a';
                        context.beginPath();
                        context.arc(0, 0, 6, 0, Math.PI * 2);
                        context.fill();
                    }} else {{
                        context.fillStyle = '#343a39';
                        context.beginPath();
                        context.ellipse(0, 4, part.rx, part.ry, 0, 0, Math.PI * 2);
                        context.fill();
                        context.strokeStyle = '#89918e';
                        context.lineWidth = 4;
                        context.stroke();
                        const head = context.createRadialGradient(-part.rx * 0.25, -part.ry * 0.35, 2, 0, 0, part.rx);
                        head.addColorStop(0, pulse ? '#fff4d0' : '#d4d1c6');
                        head.addColorStop(1, pulse ? color : '#89877f');
                        context.fillStyle = head;
                        context.beginPath();
                        context.ellipse(0, 0, part.rx * 0.86, part.ry * 0.82, 0, 0, Math.PI * 2);
                        context.fill();
                        context.strokeStyle = 'rgba(49, 52, 48, 0.55)';
                        context.lineWidth = 2;
                        context.stroke();
                    }}

                    context.fillStyle = '#e6e3d8';
                    context.font = '600 13px Trebuchet MS, sans-serif';
                    context.textAlign = 'center';
                    context.textBaseline = 'middle';
                    context.shadowColor = '#111312';
                    context.shadowBlur = 5;
                    context.fillText(part.label, 0, part.ry + 20);
                    context.restore();
                }});
            }}

            function resizeStage() {{
                const width = Math.max(stage.clientWidth, 1);
                const height = Math.max(stage.clientHeight, 1);
                canvas.width = Math.round(width * pixelRatio);
                canvas.height = Math.round(height * pixelRatio);
                drawStage();
            }}
            new ResizeObserver(resizeStage).observe(stage);
            resizeStage();

            function requestStageFrame() {{
                if (animationFrame === null) animationFrame = requestAnimationFrame(animate);
            }}

            const kickSynth = new Tone.MembraneSynth({{ pitchDecay: 0.05, octaves: 8, oscillator: {{ type: 'sine' }} }}).toDestination();
            const snareSynth = new Tone.NoiseSynth({{ noise: {{ type: 'white' }}, envelope: {{ attack: 0.001, decay: 0.2, sustain: 0 }} }}).toDestination();
            const hatSynth = new Tone.MetalSynth({{ frequency: 240, envelope: {{ attack: 0.001, decay: 0.055, release: 0.04 }}, harmonicity: 5.1, modulationIndex: 32 }}).toDestination();
            const cymbalSynth = new Tone.MetalSynth({{ frequency: 160, envelope: {{ attack: 0.001, decay: 0.8, release: 0.25 }}, harmonicity: 5.1, modulationIndex: 24 }}).toDestination();
            const tomSynth = new Tone.MembraneSynth({{ pitchDecay: 0.08, octaves: 4 }}).toDestination();
            [kickSynth, snareSynth, hatSynth, cymbalSynth, tomSynth].forEach(synth => synth.volume.value = -10);

            let player = null;
            let duration = Number(songData.duration) || 0;
            let notes = [];
            let isSeeking = false;
            let atEnd = false;
            let coachPlan = [];
            let coachBarLength = 240 / Number(songData.bpm || 120);
            let activeCoachKey = '';

            function formatTime(seconds) {{
                const safeSeconds = Math.max(0, Number(seconds) || 0);
                const minutes = Math.floor(safeSeconds / 60);
                const remaining = Math.floor(safeSeconds % 60);
                return String(minutes).padStart(2, '0') + ':' + String(remaining).padStart(2, '0');
            }}

            function buildArrangement(trackDuration) {{
                if (songData.notesComplete && Array.isArray(songData.notes)) {{
                    return songData.notes.slice().sort((left, right) => left.time - right.time);
                }}

                const beatLength = 60 / Number(songData.bpm || 120);
                const barLength = beatLength * 4;
                const barCount = Math.ceil(trackDuration / barLength);
                const empireGroove = String(songData.title || '').toLowerCase().includes('empire');
                const arrangement = [];
                const add = (bar, beat, instrument) => {{
                    const time = bar * barLength + beat * beatLength;
                    if (time < trackDuration) arrangement.push({{ time, instrument }});
                }};

                for (let bar = 0; bar < barCount; bar++) {{
                    add(bar, 0, 'kick');
                    add(bar, 2, 'kick');
                    add(bar, 1, 'snare');
                    add(bar, 3, 'snare');
                    for (let eighth = 0.5; eighth < 4; eighth += 0.5) add(bar, eighth, 'hihat');

                    if (bar === 0 && empireGroove) add(bar, 2, 'crash');
                    if (bar % 8 === 0 && !(bar === 0 && empireGroove)) add(bar, 0, 'crash');
                    if (!empireGroove && bar % 2 === 1) add(bar, 3.5, 'kick');
                    if (bar % 16 >= 8) {{
                        for (let beat = 0; beat < 4; beat++) add(bar, beat, 'ride');
                    }}

                    if (bar % 8 === 7) {{
                        add(bar, 3, 'tom1');
                        add(bar, 3.5, 'floorTom');
                        add(bar, 3.75, 'tom2');
                    }} else if (empireGroove && bar % 4 === 3) {{
                        add(bar, 3.5, 'tom1');
                    }}
                }}
                return arrangement.sort((left, right) => left.time - right.time);
            }}

            function buildCoachPlan(trackDuration) {{
                const barsPerSection = 4;
                const sectionLength = coachBarLength * barsPerSection;
                const sectionCount = Math.ceil(trackDuration / sectionLength);
                const sections = Array.from({{ length: sectionCount }}, (_, index) => ({{
                    index,
                    start: index * sectionLength,
                    end: Math.min((index + 1) * sectionLength, trackDuration),
                    hits: 0,
                    fills: 0,
                    instruments: new Set()
                }}));

                notes.forEach(note => {{
                    const sectionIndex = Math.floor(note.time / sectionLength);
                    const section = sections[sectionIndex];
                    if (!section) return;
                    section.hits++;
                    section.instruments.add(note.instrument);
                    if (['tom1', 'tom2', 'floorTom'].includes(note.instrument)) section.fills++;
                }});

                const populatedSections = sections.map(section => section.hits).filter(Boolean).sort((left, right) => left - right);
                const medianHits = populatedSections[Math.floor(populatedSections.length / 2)] || 1;
                return sections.map(section => ({{
                    ...section,
                    hard: section.fills > 0 || section.hits >= medianHits * 1.3
                }}));
            }}

            function updateCoachCue(currentTime) {{
                const nextHardSection = coachPlan.find(section => section.hard && section.end > currentTime);
                if (!nextHardSection) {{
                    const key = 'steady';
                    if (activeCoachKey !== key) {{
                        activeCoachKey = key;
                        coachEyebrow.textContent = 'LIVE COACH';
                        coachTitle.textContent = 'Groove locked';
                        coachCopy.textContent = 'Keep an even pulse and stay relaxed between accents.';
                    }}
                    return;
                }}

                const isActive = currentTime >= nextHardSection.start;
                const barsUntilStart = Math.ceil((nextHardSection.start - currentTime) / coachBarLength);
                let eyebrow;
                let title;
                let guidance;
                if (!isActive && barsUntilStart > 2) {{
                    eyebrow = 'SECTION AHEAD';
                    title = 'A challenging phrase is coming';
                    guidance = 'Keep the backbeat steady; the coach will cue your entrance.';
                }} else if (nextHardSection.fills > 0) {{
                    eyebrow = isActive ? 'TOM FILL • BAR ' + (Math.floor((currentTime - nextHardSection.start) / coachBarLength) + 1) : 'FILL IN ' + barsUntilStart + ' BARS';
                    title = isActive ? 'Move across the toms' : 'Tom fill approaching';
                    guidance = isActive ? 'Hold the pulse under the fill; land the next downbeat with the kick.' : 'Keep the groove steady, then follow the toms on the final bar.';
                }} else {{
                    eyebrow = isActive ? 'BUSY PHRASE' : 'BUSY PHRASE IN ' + barsUntilStart + ' BARS';
                    title = 'Count the subdivisions';
                    guidance = 'Keep your kick and snare even; let the cymbal pattern stay relaxed.';
                }}

                const key = [eyebrow, title, guidance].join('|');
                if (activeCoachKey !== key) {{
                    activeCoachKey = key;
                    coachEyebrow.textContent = eyebrow;
                    coachTitle.textContent = title;
                    coachCopy.textContent = guidance;
                }}
            }}

            function playDrumSound(instrument, time) {{
                if (instrument === 'kick') kickSynth.triggerAttackRelease('C1', '8n', time);
                else if (instrument === 'snare') snareSynth.triggerAttackRelease('16n', time);
                else if (instrument === 'hihat') hatSynth.triggerAttackRelease('32n', time);
                else if (instrument === 'tom1') tomSynth.triggerAttackRelease('G2', '16n', time);
                else if (instrument === 'tom2') tomSynth.triggerAttackRelease('D2', '16n', time);
                else if (instrument === 'floorTom') tomSynth.triggerAttackRelease('C2', '8n', time);
                else if (instrument === 'crash' || instrument === 'ride') cymbalSynth.triggerAttackRelease('8n', time);
            }}

            function triggerHit(instrument, time) {{
                const part = parts[instrument];
                if (!part) return;
                part.pulse = 1;
                playDrumSound(instrument, time);
            }}

            function scheduleArrangement() {{
                Tone.Transport.cancel(0);
                notes = buildArrangement(duration);
                notes.forEach(note => Tone.Transport.schedule(time => triggerHit(note.instrument, time), note.time));
                coachPlan = buildCoachPlan(duration);
                updateCoachCue(Tone.Transport.seconds);
            }}

            function setupPlayer() {{
                if (!songData.audioUrl) {{
                    duration = duration || 180;
                    scrubber.max = duration;
                    scheduleArrangement();
                    playButton.disabled = false;
                    status.style.display = 'none';
                    return;
                }}

                player = new Tone.Player({{
                    url: songData.audioUrl,
                    autostart: false,
                    onload: () => {{
                        duration = player.buffer.duration;
                        scrubber.max = duration;
                        scheduleArrangement();
                        playButton.disabled = false;
                        status.style.display = 'none';
                    }},
                    onerror: () => {{
                        status.textContent = 'Track audio could not be loaded.';
                        playButton.disabled = true;
                    }}
                }}).toDestination();
                player.volume.value = -4;
                player.sync().start(0);
            }}
            setupPlayer();

            function requestStageFrame() {{
                if (animationFrame === null) animationFrame = requestAnimationFrame(animate);
            }}

            function animate(now) {{
                animationFrame = null;
                const isPlaying = Tone.Transport.state === 'started';
                const hasPulse = Object.values(parts).some(part => part.pulse > 0.01);
                if ((isPlaying || hasPulse) && now - previousFrame < 1000 / 30) {{
                    requestStageFrame();
                    return;
                }}
                const delta = Math.min((now - previousFrame) / 1000, 0.05);
                previousFrame = now;
                let currentTime = Tone.Transport.seconds;
                if (isPlaying && !isSeeking) {{
                    scrubber.value = currentTime;
                    if (duration > 0 && currentTime >= duration) {{
                        Tone.Transport.stop();
                        Tone.Transport.seconds = duration;
                        currentTime = duration;
                        atEnd = true;
                        playButton.textContent = 'Play Again';
                    }}
                }}
                timeDisplay.textContent = formatTime(atEnd ? duration : currentTime) + ' / ' + formatTime(duration);
                updateCoachCue(currentTime);

                Object.values(parts).forEach(part => {{
                    part.pulse = Math.max(0, part.pulse - delta * 2.7);
                }});
                drawStage();
                if (Tone.Transport.state === 'started' || Object.values(parts).some(part => part.pulse > 0.01)) {{
                    requestStageFrame();
                }}
            }}
            requestStageFrame();

            scrubber.onpointerdown = () => {{ isSeeking = true; }};
            scrubber.onpointerup = () => {{ isSeeking = false; }};
            scrubber.oninput = () => {{
                const seekTime = Number(scrubber.value);
                Tone.Transport.seconds = seekTime;
                atEnd = false;
                timeDisplay.textContent = formatTime(seekTime) + ' / ' + formatTime(duration);
                updateCoachCue(seekTime);
                requestStageFrame();
            }};

            playButton.onclick = async () => {{
                await Tone.start();
                if (Tone.Transport.state === 'started') {{
                    Tone.Transport.pause();
                    playButton.textContent = 'Resume';
                }} else {{
                    if (atEnd) Tone.Transport.seconds = 0;
                    atEnd = false;
                    Tone.Transport.loop = false;
                    Tone.Transport.bpm.value = songData.bpm || 120;
                    Tone.Transport.start();
                    playButton.textContent = 'Pause';
                }}
                requestStageFrame();
            }};

            document.getElementById('stopBtn').onclick = () => {{
                Tone.Transport.stop();
                Tone.Transport.seconds = 0;
                atEnd = false;
                scrubber.value = 0;
                playButton.textContent = 'Play Track';
                requestStageFrame();
            }};
        </script>
    </body>
    </html>
    """
    html_comp.html(js_code, height=700)