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
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/0.152.2/three.min.js" onerror="window.visualizerLibraryLoadFailure = 'Three.js';"></script>
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
            if (!window.THREE || !window.Tone) {{
                const failedLibrary = window.visualizerLibraryLoadFailure || 'Visualizer libraries';
                status.textContent = failedLibrary + ' could not load. Check your internet connection and reload.';
                throw new Error(failedLibrary + ' failed to load.');
            }}
            const scene = new THREE.Scene();
            scene.background = new THREE.Color('#111312');
            scene.fog = new THREE.Fog('#111312', 12, 25);

            const camera = new THREE.PerspectiveCamera(39, 16 / 9, 0.1, 60);
            camera.position.set(0, 5.2, 9.3);
            camera.lookAt(0, 1.25, 0);

            let renderer;
            try {{
                renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: false, powerPreference: 'low-power' }});
            }} catch (error) {{
                status.textContent = 'WebGL is unavailable. Enable browser hardware acceleration and reload.';
                throw error;
            }}
            renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
            renderer.outputColorSpace = THREE.SRGBColorSpace;
            renderer.toneMapping = THREE.ACESFilmicToneMapping;
            renderer.toneMappingExposure = 1.15;
            stage.insertBefore(renderer.domElement, status);
            let animationFrame = null;
            let previousFrame = performance.now();

            const ambient = new THREE.HemisphereLight('#dce5ec', '#27231e', 2.1);
            scene.add(ambient);
            const keyLight = new THREE.DirectionalLight('#f6e9ce', 3.2);
            keyLight.position.set(-4, 8, 5);
            scene.add(keyLight);
            const rimLight = new THREE.DirectionalLight('#82a9a8', 1.5);
            rimLight.position.set(4, 5, -5);
            scene.add(rimLight);

            const floor = new THREE.Mesh(
                new THREE.PlaneGeometry(40, 40),
                new THREE.MeshStandardMaterial({{ color: '#202321', roughness: 0.9, metalness: 0.08 }})
            );
            floor.rotation.x = -Math.PI / 2;
            floor.position.y = -0.03;
            scene.add(floor);

            const rug = new THREE.Mesh(
                new THREE.CircleGeometry(4.1, 72),
                new THREE.MeshStandardMaterial({{ color: '#292b28', roughness: 0.98, metalness: 0.02 }})
            );
            rug.rotation.x = -Math.PI / 2;
            rug.position.y = 0.005;
            rug.scale.set(1.35, 0.82, 1);
            scene.add(rug);

            const chrome = new THREE.MeshStandardMaterial({{ color: '#89918e', metalness: 0.84, roughness: 0.28 }});
            const darkMetal = new THREE.MeshStandardMaterial({{ color: '#343a39', metalness: 0.78, roughness: 0.34 }});
            const shellMaterial = new THREE.MeshStandardMaterial({{ color: '#343b3b', metalness: 0.58, roughness: 0.3 }});
            const headMaterial = new THREE.MeshStandardMaterial({{ color: '#c8c5b9', metalness: 0.12, roughness: 0.66 }});
            const cymbalMaterial = new THREE.MeshStandardMaterial({{ color: '#b38a47', metalness: 0.82, roughness: 0.25 }});
            const partColors = {{
                kick: '#4bc9dd', snare: '#ee667a', hihat: '#e2bc56',
                tom1: '#71c28a', tom2: '#65aa7a', floorTom: '#72c29a',
                crash: '#e48c4e', ride: '#d6ad58'
            }};
            const parts = {{}};

            function makePart(key, x, z) {{
                const group = new THREE.Group();
                group.position.set(x, 0, z);
                scene.add(group);
                const light = new THREE.SpotLight(partColors[key], 0, 8, Math.PI / 6, 0.68, 1.4);
                light.position.set(x, 5.1, z);
                light.target.position.set(x, 0.55, z);
                scene.add(light, light.target);
                const beam = new THREE.Mesh(
                    new THREE.ConeGeometry(0.95, 4.1, 28, 1, true),
                    new THREE.MeshBasicMaterial({{ color: partColors[key], transparent: true, opacity: 0, depthWrite: false, side: THREE.DoubleSide, blending: THREE.AdditiveBlending }})
                );
                beam.position.set(x, 3.4, z);
                beam.rotation.x = Math.PI;
                scene.add(beam);
                const part = {{ group, light, beam, pulse: 0, meshes: [] }};
                parts[key] = part;
                return part;
            }}

            function addSupport(group, x, z, height, radius = 0.025) {{
                const pole = new THREE.Mesh(new THREE.CylinderGeometry(radius, radius * 1.3, height, 10), chrome);
                pole.position.set(x, height / 2, z);
                group.add(pole);
                const feet = new THREE.Mesh(new THREE.CylinderGeometry(0.21, 0.21, 0.035, 20), darkMetal);
                feet.position.set(x, 0.035, z);
                group.add(feet);
            }}

            function addDrum(key, x, y, z, radius, depth, axisTowardViewer = false) {{
                const part = makePart(key, x, z);
                const drum = new THREE.Group();
                drum.position.y = y;
                if (axisTowardViewer) drum.rotation.x = Math.PI / 2;
                part.group.add(drum);
                const shell = new THREE.Mesh(new THREE.CylinderGeometry(radius, radius, depth, 40, 1), shellMaterial);
                drum.add(shell);
                const head = new THREE.Mesh(new THREE.CircleGeometry(radius * 0.91, 40), headMaterial);
                head.position.y = depth / 2 + 0.006;
                head.rotation.x = -Math.PI / 2;
                drum.add(head);
                const rim = new THREE.Mesh(new THREE.TorusGeometry(radius * 0.96, 0.035, 8, 48), chrome);
                rim.position.y = depth / 2 + 0.025;
                rim.rotation.x = -Math.PI / 2;
                drum.add(rim);
                if (axisTowardViewer) {{
                    head.position.set(0, depth / 2 + 0.008, 0);
                    rim.position.set(0, depth / 2 + 0.025, 0);
                }}
                part.meshes.push(head, rim);
                const legs = axisTowardViewer ? 0 : 2;
                for (let index = 0; index < legs; index++) {{
                    const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.022, 0.032, y - 0.1, 8), chrome);
                    leg.position.set((index ? 1 : -1) * radius * 0.6, -(y - 0.1) / 2, 0);
                    drum.add(leg);
                }}
                return part;
            }}

            function addCymbal(key, x, z, y, radius) {{
                const part = makePart(key, x, z);
                addSupport(part.group, 0, 0, y, 0.022);
                const plate = new THREE.Mesh(new THREE.CylinderGeometry(radius * 0.94, radius, 0.055, 48), cymbalMaterial);
                plate.position.y = y;
                part.group.add(plate);
                const bell = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.2, 0.11, 28), cymbalMaterial);
                bell.position.y = y + 0.07;
                part.group.add(bell);
                part.meshes.push(plate, bell);
                return part;
            }}

            addDrum('kick', 0, 0.78, 0.75, 0.79, 0.62, true);
            addDrum('snare', -1.55, 1.15, 0.2, 0.48, 0.25);
            addDrum('tom1', -0.76, 1.83, -0.15, 0.42, 0.34);
            addDrum('tom2', 0.12, 1.92, -0.2, 0.44, 0.36);
            addDrum('floorTom', 1.35, 1.08, -0.15, 0.56, 0.52);
            addCymbal('hihat', -2.35, 0.25, 2.02, 0.61);
            addCymbal('crash', -1.75, -0.5, 3.12, 0.82);
            addCymbal('ride', 2.05, -0.55, 2.95, 0.9);

            const throne = new THREE.Mesh(new THREE.CylinderGeometry(0.48, 0.52, 0.16, 32), darkMetal);
            throne.position.set(0, 1.05, -1.42);
            scene.add(throne);
            const throneStem = new THREE.Mesh(new THREE.CylinderGeometry(0.055, 0.075, 0.94, 12), chrome);
            throneStem.position.set(0, 0.55, -1.42);
            scene.add(throneStem);
            const pedalBoard = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.08, 0.54), darkMetal);
            pedalBoard.position.set(0, 0.09, 1.48);
            pedalBoard.rotation.x = -0.18;
            scene.add(pedalBoard);

            function addLabel(text, x, y, z) {{
                const labelCanvas = document.createElement('canvas');
                labelCanvas.width = 256;
                labelCanvas.height = 64;
                const labelContext = labelCanvas.getContext('2d');
                labelContext.fillStyle = 'rgba(14, 16, 15, 0.8)';
                labelContext.beginPath();
                labelContext.roundRect(4, 4, 248, 56, 12);
                labelContext.fill();
                labelContext.fillStyle = '#e6e3d8';
                labelContext.font = '600 27px Trebuchet MS, sans-serif';
                labelContext.textAlign = 'center';
                labelContext.textBaseline = 'middle';
                labelContext.fillText(text, 128, 32);
                const texture = new THREE.CanvasTexture(labelCanvas);
                texture.colorSpace = THREE.SRGBColorSpace;
                const sprite = new THREE.Sprite(new THREE.SpriteMaterial({{ map: texture, transparent: true, depthTest: false }}));
                sprite.position.set(x, y, z);
                sprite.scale.set(0.85, 0.22, 1);
                scene.add(sprite);
            }}
            addLabel('KICK', 0, 0.35, 1.65);
            addLabel('SNARE', -1.55, 1.9, 0.3);
            addLabel('TOM 1', -0.76, 2.43, -0.15);
            addLabel('TOM 2', 0.12, 2.55, -0.2);
            addLabel('FLOOR TOM', 1.35, 1.75, -0.15);
            addLabel('HI-HAT', -2.35, 2.55, 0.25);
            addLabel('CRASH', -1.75, 3.65, -0.5);
            addLabel('RIDE', 2.05, 3.5, -0.55);

            function resizeStage() {{
                const width = Math.max(stage.clientWidth, 1);
                const height = Math.max(stage.clientHeight, 1);
                renderer.setSize(width, height, false);
                camera.aspect = width / height;
                camera.position.x = width < 560 ? 0 : -0.15;
                camera.position.z = width < 560 ? 10.8 : 9.3;
                camera.lookAt(0, 1.25, 0);
                camera.updateProjectionMatrix();
                requestStageFrame();
            }}
            new ResizeObserver(resizeStage).observe(stage);
            resizeStage();

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
                    part.light.intensity = part.pulse * 34;
                    part.beam.material.opacity = part.pulse * 0.16;
                    part.meshes.forEach(mesh => {{
                        mesh.material.emissive.set(part.pulse > 0 ? part.light.color : '#000000');
                        mesh.material.emissiveIntensity = part.pulse * 0.72;
                    }});
                }});
                renderer.render(scene, camera);
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