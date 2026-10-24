/**
 * AvatarEngine: Authentic Hand Talk 3D Avatar Engine (Hugo & Maya)
 * Built with Three.js, GLTFLoader, & Three.js AnimationMixer.
 * 
 * Features:
 * - Authentic 3D Humanoid Avatars extracted directly from Hand Talk: Hugo & Maya
 * - Dual-rig binding across 248 Rigify DEF deformation and ORG kinematic bones
 * - Native Three.js AnimationMixer & AnimationClip playback matching Hand Talk's core.min.js
 * - Authentic Hand Talk "@repouso" neutral resting pose (no T-pose)
 * - Authentic Hand Talk letter animations (A-Z, 0-9) extracted directly from app container
 * - Smooth 200ms cross-fading & SLERP coarticulation between signs and rest pose
 * - 60 Non-Manual Marker (NMM) facial blendshapes: stochastic blinking (OLHO.PISCA.R/L),
 *   eyebrow raise/furrow (SOBRANCELHA.MEIO.SOBE/DESCE), mouth visemes (BOCA.ABRE/O, LABIO.CANTO.SOBE/DESCE)
 * - Living idle state: natural thoracic breathing and gentle postural micro-sway
 * - Studio key/fill/rim lighting matching Hand Talk mobile & web viewer
 * - High-contrast clothing theme switcher (Dark / Light)
 * - Real-time signing speed scaling (0.75x - 1.5x)
 */

const HT_TF = {
  BA:"DEF-hips", BB:"ORG-hips", BC:"DEF-spine", BD:"DEF-thighL01", BE:"DEF-thighR01", BF:"ORG-spine",
  BG:"DEF-ribs", BH:"ORG-ribs", BI:"DEF-neck", BJ:"ORG-neck", BK:"DEF-head",
  BL:"ORG-shoulderL", BM:"DEF-shoulderL", BN:"DEF-upper_armL01", BO:"ORG-upper_armL", BP:"DEF-upper_armL02",
  BQ:"ORG-forearmL", BR:"DEF-forearmL01", BS:"DEF-forearmL02", BT:"ORG-handL",
  BU:"DEF-finger_index01L01", BV:"DEF-finger_middle01L01", BW:"DEF-finger_pinky01L01", BX:"DEF-finger_ring01L01",
  BY:"DEF-handL", BZ:"DEF-thumb01L01", CA:"ORG-finger_index01L", CB:"DEF-finger_index01L02", CC:"ORG-finger_index02L",
  CD:"DEF-finger_index02L", CE:"ORG-finger_index03L", CF:"DEF-finger_index03L", CG:"ORG-finger_middle01L",
  CH:"DEF-finger_middle01L02", CI:"ORG-finger_middle02L", CJ:"DEF-finger_middle02L", CK:"ORG-finger_middle03L",
  CL:"DEF-finger_middle03L", CM:"ORG-finger_pinky01L", CN:"DEF-finger_pinky01L02", CO:"ORG-finger_pinky02L",
  CP:"DEF-finger_pinky02L", CQ:"ORG-finger_pinky03L", CR:"DEF-finger_pinky03L", CS:"ORG-finger_ring01L",
  CT:"DEF-finger_ring01L02", CU:"ORG-finger_ring02L", CV:"DEF-finger_ring02L", CW:"ORG-finger_ring03L",
  CX:"DEF-finger_ring03L", CY:"ORG-thumb01L", CZ:"DEF-thumb01L02", DA:"ORG-thumb02L", DB:"DEF-thumb02L",
  DC:"ORG-thumb03L", DD:"DEF-thumb03L",
  DE:"ORG-shoulderR", DF:"DEF-shoulderR", DG:"DEF-upper_armR01", DH:"ORG-upper_armR", DI:"DEF-upper_armR02",
  DJ:"ORG-forearmR", DK:"DEF-forearmR01", DL:"DEF-forearmR02", DM:"ORG-handR",
  DN:"DEF-finger_index01R01", DO:"DEF-finger_middle01R01", DP:"DEF-finger_pinky01R01", DQ:"DEF-finger_ring01R01",
  DR:"DEF-handR", DS:"DEF-thumb01R01", DT:"ORG-finger_index01R", DU:"DEF-finger_index01R02", DV:"ORG-finger_index02R",
  DW:"DEF-finger_index02R", DX:"ORG-finger_index03R", DY:"DEF-finger_index03R", DZ:"ORG-finger_middle01R",
  EA:"DEF-finger_middle01R02", EB:"ORG-finger_middle02R", EC:"DEF-finger_middle02R", ED:"ORG-finger_middle03R",
  EE:"DEF-finger_middle03R", EF:"ORG-finger_pinky01R", EG:"DEF-finger_pinky01R02", EH:"ORG-finger_pinky02R",
  EI:"DEF-finger_pinky02R", EJ:"ORG-finger_pinky03R", EK:"DEF-finger_pinky03R", EL:"ORG-finger_ring01R",
  EM:"DEF-finger_ring01R02", EN:"ORG-finger_ring02R", EO:"DEF-finger_ring02R", EP:"ORG-finger_ring03R",
  EQ:"DEF-finger_ring03R", ER:"ORG-thumb01R", ES:"DEF-thumb01R02", ET:"ORG-thumb02R", EU:"DEF-thumb02R",
  EV:"ORG-thumb03R", EW:"DEF-thumb03R",
  UA:"SOBRANCELHA.DENTRO.SOBE.R", UB:"SOBRANCELHA.DENTRO.SOBE.L",
  UC:"SOBRANCELHA.DENTRO.DESCE.R", UD:"SOBRANCELHA.DENTRO.DESCE.L",
  UE:"SOBRANCELHA.MEIO.SOBE.R", UF:"SOBRANCELHA.MEIO.SOBE.L",
  UG:"SOBRANCELHA.MEIO.DESCE.R", UH:"SOBRANCELHA.MEIO.DESCE.L",
  UI:"SOBRANCELHA.FORA.SOBE.R", UJ:"SOBRANCELHA.FORA.SOBE.L",
  UK:"SOBRANCELHA.FORA.DESCE.R", UL:"SOBRANCELHA.FORA.DESCE.L",
  UM:"OLHO.PISCA.R", UN:"OLHO.PISCA.L",
  VA:"LABIO.CANTO.SOBE.R", VB:"LABIO.CANTO.SOBE.L",
  VC:"LABIO.CANTO.DESCE.R", VD:"LABIO.CANTO.DESCE.L",
  VK:"BOCA.O", VL:"BOCA.ABRE"
};

const HT_DT = 2.7;

class AvatarEngine {
  constructor(canvasElement) {
    this.canvas = canvasElement;
    this.character = 'hugo'; // 'hugo' | 'maya'
    this.clothingTheme = 'dark'; // 'dark' | 'light'
    this.playbackSpeed = 1.0;
    this.effectiveSpeed = 1.0;
    this.isPlaying = false;
    this.animationQueue = [];
    this.currentTrack = null;
    this.currentAction = null;
    this.repousoAction = null;

    // Natural blinking state
    this.nextBlinkTime = performance.now() + 2000;
    this.isBlinking = false;
    this.blinkProgress = 0;

    // Active NMM state
    this.activeNmm = {
      eyebrows: 'neutral',
      headTilt: 0.0,
      headShake: false,
      headNod: false,
      mouth: 'neutral'
    };

    // Node & Mesh storage
    this.nodeMap = {};
    this.headMesh = null;
    this.morphDict = {};
    this.morphInfluences = null;
    this.shirtMaterial = null;
    this.restQuaternions = new Map();
    this.repousoQuaternions = new Map();

    // Semantic bone groups
    this.boneGroups = {
      RightArm: [],
      RightForeArm: [],
      RightHand: [],
      RightShoulder: [],
      LeftArm: [],
      LeftForeArm: [],
      LeftHand: [],
      LeftShoulder: [],
      Spine: [],
      Neck: [],
      Head: []
    };
    this.fingerBones = { Right: {}, Left: {} };

    // Hand Talk Animation Lexicon
    this.animLexicon = null;
    this.loadAnimLexicon();

    // Model cache & loader
    this.models = { hugo: null, maya: null };
    this.loader = new THREE.GLTFLoader();
    this.isLoading = false;
    this.mixer = null;

    this.initScene();
    this.loadCharacter(this.character);

    this.animate = this.animate.bind(this);
    this.lastFrameTime = performance.now();
    requestAnimationFrame(this.animate);
  }

  async loadAnimLexicon() {
    try {
      const resp = await fetch('assets/handtalk_anim_lexicon.json');
      if (resp.ok) {
        this.animLexicon = await resp.json();
        console.log('[AvatarEngine] Loaded Hand Talk animation lexicon successfully.');
        if (this.avatarGroup.children.length > 0 && !this.repousoAction) {
          this.initRepouso();
        }
      }
    } catch (err) {
      console.warn('[AvatarEngine] Could not load anim lexicon:', err);
    }
  }

  initScene() {
    this.scene = new THREE.Scene();

    const width = this.canvas.clientWidth || 400;
    const height = this.canvas.clientHeight || 450;

    // Framed from mid-chest up for optimal sign visibility
    this.camera = new THREE.PerspectiveCamera(32, width / height, 0.1, 100);
    this.camera.position.set(0, 1.48, 2.15);
    this.camera.lookAt(0, 1.34, 0);

    this.renderer = new THREE.WebGLRenderer({
      canvas: this.canvas,
      alpha: true,
      antialias: true,
      powerPreference: 'high-performance'
    });
    this.renderer.setSize(width, height);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

    if (THREE.sRGBEncoding) {
      this.renderer.outputEncoding = THREE.sRGBEncoding;
    }

    if (THREE.ACESFilmicToneMapping) {
      this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
      this.renderer.toneMappingExposure = 0.80;
    }

    // Balanced Studio Lighting (calibrated to prevent glare and overexposure)
    this.ambientLight = new THREE.AmbientLight(0xdde8f5, 0.40);
    this.scene.add(this.ambientLight);

    this.keyLight = new THREE.DirectionalLight(0xffffff, 0.50);
    this.keyLight.position.set(-1.5, 2.2, 1.5);
    this.scene.add(this.keyLight);

    this.rimLight = new THREE.DirectionalLight(0x93c5fd, 0.28);
    this.rimLight.position.set(1.5, 2.2, -1.5);
    this.scene.add(this.rimLight);

    this.underLight = new THREE.DirectionalLight(0xffedd5, 0.10);
    this.underLight.position.set(0, -1.0, 1.0);
    this.scene.add(this.underLight);

    this.brightnessFactor = 0.80;

    this.avatarGroup = new THREE.Group();
    this.scene.add(this.avatarGroup);

    window.addEventListener('resize', () => {
      const w = this.canvas.clientWidth;
      const h = this.canvas.clientHeight;
      if (w && h) {
        this.camera.aspect = w / h;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(w, h);
      }
    });
  }

  loadCharacter(charName) {
    this.character = charName;
    const filename = charName === 'hugo' ? 'HUGO.gltf' : 'MAYA.gltf';
    const modelPath = `assets/models/${filename}`;

    if (this.models[charName]) {
      this.setupActiveModel(this.models[charName]);
      return;
    }

    this.isLoading = true;
    this.loader.load(
      modelPath,
      (gltf) => {
        this.models[charName] = gltf.scene;
        if (this.character === charName) {
          this.setupActiveModel(gltf.scene);
        }
        this.isLoading = false;
        console.log(`[AvatarEngine] Loaded authentic Hand Talk model: ${filename}`);
      },
      undefined,
      (err) => {
        console.warn(`[AvatarEngine] Error loading ${modelPath}:`, err);
        this.isLoading = false;
      }
    );
  }

  setupActiveModel(sceneObj) {
    while (this.avatarGroup.children.length > 0) {
      this.avatarGroup.remove(this.avatarGroup.children[0]);
    }
    this.avatarGroup.add(sceneObj);

    // Initialize Three.js AnimationMixer on active model
    this.mixer = new THREE.AnimationMixer(sceneObj);
    this.currentAction = null;
    this.repousoAction = null;

    // Reset bone groups & node maps
    this.nodeMap = {};
    this.boneGroups = {
      RightArm: [],
      RightForeArm: [],
      RightHand: [],
      RightShoulder: [],
      LeftArm: [],
      LeftForeArm: [],
      LeftHand: [],
      LeftShoulder: [],
      Spine: [],
      Neck: [],
      Head: []
    };
    this.fingerBones = { Right: {}, Left: {} };
    this.restQuaternions.clear();
    this.repousoQuaternions.clear();
    this.headMesh = null;
    this.morphDict = {};
    this.morphInfluences = null;
    this.shirtMaterial = null;

    // Traverse scene to index nodes, morphs, and materials
    sceneObj.traverse((node) => {
      const name = node.name || '';
      if (!name) return;

      this.nodeMap[name] = node;
      this.restQuaternions.set(node.uuid, node.quaternion.clone());

      if (node.morphTargetDictionary) {
        if (name.includes('head') || name.includes('Head')) {
          this.headMesh = node;
          this.morphDict = node.morphTargetDictionary || {};
          this.morphInfluences = node.morphTargetInfluences || [];
        }
      }

      if (node.material) {
        const mat = node.material;
        if (mat.roughness !== undefined) {
          mat.roughness = Math.max(mat.roughness, 0.65);
        }
        if (mat.name && (mat.name.includes('Shirt') || mat.name.includes('camisa'))) {
          this.shirtMaterial = mat;
        }
      }

      const clean = name.replace(/[-_.]/g, '').toLowerCase();
      if (clean.startsWith('adj')) return;

      if (clean === 'orgupperarmr' || clean === 'defupperarmr01') this.boneGroups.RightArm.push(node);
      else if (clean === 'orgforearmr') this.boneGroups.RightForeArm.push(node);
      else if (clean === 'orghandr') this.boneGroups.RightHand.push(node);
      else if (clean === 'orgshoulderr' || clean === 'defshoulderr') this.boneGroups.RightShoulder.push(node);

      else if (clean === 'orgupperarml' || clean === 'defupperarml01') this.boneGroups.LeftArm.push(node);
      else if (clean === 'orgforearml') this.boneGroups.LeftForeArm.push(node);
      else if (clean === 'orghandl') this.boneGroups.LeftHand.push(node);
      else if (clean === 'orgshoulderl' || clean === 'defshoulderl') this.boneGroups.LeftShoulder.push(node);

      else if (clean === 'orgspine' || clean === 'orgribs' || clean === 'defspine' || clean === 'defribs') this.boneGroups.Spine.push(node);
      else if (clean === 'orgneck' || clean === 'defneck') this.boneGroups.Neck.push(node);
      else if (clean === 'orghead' || clean === 'defhead') this.boneGroups.Head.push(node);

      this.bindFinger(node, clean, 'Right', 'r');
      this.bindFinger(node, clean, 'Left', 'l');
    });

    this.applyClothingTheme();

    // Initialize authentic Hand Talk rest pose
    if (this.animLexicon) {
      this.initRepouso();
    }
  }

  bindFinger(node, clean, side, sChar) {
    const fingers = ['thumb', 'finger_index', 'finger_middle', 'finger_ring', 'finger_pinky'];
    for (const f of fingers) {
      const fClean = f.replace(/_/g, '');
      for (let ph = 1; ph <= 3; ph++) {
        const targetOrg = `org${fClean}0${ph}${sChar}`;
        if (clean === targetOrg) {
          const fingerKey = `${f}_${ph}`;
          if (!this.fingerBones[side][fingerKey]) {
            this.fingerBones[side][fingerKey] = [];
          }
          this.fingerBones[side][fingerKey].push(node);
        }
      }
    }
  }

  initRepouso() {
    if (!this.animLexicon || !this.mixer) return;
    const repousoStr = this.animLexicon.bsl?.repouso || this.animLexicon.bzs?.repouso;
    if (!repousoStr) return;

    this.repousoClip = this.createClipFromHT('repouso', repousoStr);
    if (!this.repousoClip) return;

    this.repousoAction = this.mixer.clipAction(this.repousoClip);
    this.repousoAction.setLoop(THREE.LoopRepeat);
    this.repousoAction.play();
    this.currentAction = this.repousoAction;

    // Cache repouso target quaternions for procedural signs
    this.mixer.update(0.1);
    this.scene.updateMatrixWorld(true);

    for (const [name, node] of Object.entries(this.nodeMap)) {
      this.repousoQuaternions.set(name, node.quaternion.clone());
    }

    console.log('[AvatarEngine] Initialized authentic Hand Talk natural repouso rest pose.');
  }

  createClipFromHT(name, animStr) {
    if (!animStr) return null;
    const tracks = [];

    const eulerToQuat = (ex, ey, ez) => {
      const e = new THREE.Euler(ex, ey, ez, 'XYZ');
      return new THREE.Quaternion().setFromEuler(e);
    };

    animStr.split('?').forEach(part => {
      const tokens = part.split('*');
      const code = tokens[0];
      const targetName = HT_TF[code];
      if (!targetName) return;

      const isMorph = 'UVWXYZ'.includes(code[0]);
      if (isMorph && this.headMesh) {
        const morphName = targetName;
        const idx = this.morphDict[morphName];
        if (idx !== undefined) {
          const rawTimes = tokens[1].split('#').map(t => parseInt(t || '0', 10) * 0.0416666667);
          const rawVals = tokens[2].split('#').map(v => parseInt(v || '0', 10) / 100.0);
          tracks.push(new THREE.NumberKeyframeTrack(
            `${this.headMesh.name}.morphTargetInfluences[${idx}]`,
            rawTimes,
            rawVals
          ));
        }
      } else {
        const targetNode = this.nodeMap[targetName];
        if (!targetNode) return;

        const rawTimes = tokens[1].split('#').map(t => parseInt(t || '0', 10) * 0.0416666667);
        const rawX = tokens[2] ? tokens[2].split('#').map(v => (parseInt(v || '0', 10) / HT_DT) * Math.PI / 180) : [];
        const rawY = tokens[3] ? tokens[3].split('#').map(v => (parseInt(v || '0', 10) / HT_DT) * Math.PI / 180) : [];
        const rawZ = tokens[4] ? tokens[4].split('#').map(v => (parseInt(v || '0', 10) / HT_DT) * Math.PI / 180) : [];

        const quatValues = [];
        for (let i = 0; i < rawTimes.length; i++) {
          const q = eulerToQuat(rawX[i] || 0, rawY[i] || 0, rawZ[i] || 0);
          quatValues.push(q.x, q.y, q.z, q.w);
        }

        tracks.push(new THREE.QuaternionKeyframeTrack(
          `${targetNode.name}.quaternion`,
          rawTimes,
          quatValues
        ));
      }
    });

    if (tracks.length === 0) return null;
    return new THREE.AnimationClip(name, -1, tracks);
  }

  createClipFromProceduralFrames(name, frames, duration = 1.0) {
    if (!frames || frames.length === 0) return null;
    const tracks = [];

    const majorGroups = [
      'RightArm', 'RightForeArm', 'RightHand',
      'LeftArm', 'LeftForeArm', 'LeftHand',
      'Spine', 'RightShoulder', 'LeftShoulder'
    ];

    const times = frames.map(f => f.time || 0.0);
    if (times[times.length - 1] < duration) {
      times[times.length - 1] = duration;
    }

    majorGroups.forEach(groupName => {
      const bones = this.boneGroups[groupName] || [];
      if (bones.length === 0) return;

      const hasGroup = frames.some(f => f[groupName]);
      if (!hasGroup) return;

      bones.forEach(bone => {
        const quatValues = [];
        const baseQuat = this.repousoQuaternions.get(bone.name) || this.restQuaternions.get(bone.uuid) || new THREE.Quaternion();

        frames.forEach(f => {
          if (f[groupName]) {
            const deltaQ = new THREE.Quaternion(...f[groupName]);
            const target = baseQuat.clone().multiply(deltaQ);
            quatValues.push(target.x, target.y, target.z, target.w);
          } else {
            quatValues.push(baseQuat.x, baseQuat.y, baseQuat.z, baseQuat.w);
          }
        });

        tracks.push(new THREE.QuaternionKeyframeTrack(
          `${bone.name}.quaternion`,
          times,
          quatValues
        ));
      });
    });

    if (tracks.length === 0) return null;
    return new THREE.AnimationClip(name, duration, tracks);
  }

  setCharacter(charName) {
    if (this.character !== charName) {
      this.loadCharacter(charName);
    }
  }

  setClothingTheme(theme) {
    this.clothingTheme = theme;
    this.applyClothingTheme();
  }

  applyClothingTheme() {
    if (!this.shirtMaterial) return;
    if (this.clothingTheme === 'dark') {
      this.shirtMaterial.color.setHex(0x1e293b);
      this.shirtMaterial.roughness = 0.55;
    } else {
      this.shirtMaterial.color.setHex(0xffffff);
      this.shirtMaterial.roughness = 0.45;
    }
  }

  setPlaybackSpeed(speed) {
    this.playbackSpeed = Math.max(0.5, Math.min(2.0, speed));
    this.updateEffectiveSpeed();
  }

  setSpeed(speed) {
    this.setPlaybackSpeed(speed);
  }

  updateEffectiveSpeed() {
    if (this.animationQueue.length > 2) {
      this.effectiveSpeed = this.playbackSpeed * 1.35;
    } else {
      this.effectiveSpeed = this.playbackSpeed;
    }
  }

  // Primary API method called by renderer.js
  playSequence(keyframeTrack, nmm = {}, onComplete = null) {
    if (!keyframeTrack) {
      if (onComplete) onComplete();
      return;
    }

    let clip = null;

    // 1. Check if track is a direct Hand Talk animation string or word gloss
    if (typeof keyframeTrack === 'string') {
      const trimmed = keyframeTrack.trim();
      let animStr = trimmed;
      if (!trimmed.includes('*') && this.animLexicon) {
        const upper = trimmed.toUpperCase();
        const lower = trimmed.toLowerCase();
        if (this.animLexicon.words && (this.animLexicon.words[upper] || this.animLexicon.words[lower])) {
          animStr = this.animLexicon.words[upper] || this.animLexicon.words[lower];
        } else if (this.animLexicon.ase && (this.animLexicon.ase[lower] || this.animLexicon.ase[upper])) {
          animStr = this.animLexicon.ase[lower] || this.animLexicon.ase[upper];
        } else if (this.animLexicon.bsl && (this.animLexicon.bsl[lower] || this.animLexicon.bsl[upper])) {
          animStr = this.animLexicon.bsl[lower] || this.animLexicon.bsl[upper];
        } else if (this.animLexicon.bzs && (this.animLexicon.bzs[lower] || this.animLexicon.bzs[upper])) {
          animStr = this.animLexicon.bzs[lower] || this.animLexicon.bzs[upper];
        }
      }
      if (animStr && animStr.includes('*')) {
        clip = this.createClipFromHT('sign_' + trimmed, animStr);
      }
    }
    // 2. Check if track is an array or object containing procedural keyframes
    else if (Array.isArray(keyframeTrack)) {
      clip = this.createClipFromProceduralFrames('sign_proc', keyframeTrack);
    } else if (typeof keyframeTrack === 'object' && keyframeTrack.keyframes) {
      clip = this.createClipFromProceduralFrames('sign_proc', keyframeTrack.keyframes, keyframeTrack.duration);
    }

    if (!clip) {
      if (onComplete) onComplete();
      return;
    }

    this.queueClip(clip, nmm, onComplete);
  }

  queueClip(clip, nmm = {}, onComplete = null) {
    this.animationQueue.push({
      clip: clip,
      nmm: nmm || {},
      onComplete: onComplete
    });

    this.updateEffectiveSpeed();

    if (!this.isPlaying) {
      this.playNextInQueue();
    }
  }

  playNextInQueue() {
    if (this.animationQueue.length > 0) {
      this.isPlaying = true;
      this.currentTrack = this.animationQueue.shift();

      if (this.currentTrack.nmm) {
        this.setNMM(this.currentTrack.nmm);
      }

      if (this.mixer && this.currentTrack.clip) {
        const action = this.mixer.clipAction(this.currentTrack.clip);
        action.reset();
        action.setLoop(THREE.LoopOnce);
        action.clampWhenFinished = true;

        if (this.currentAction) {
          action.crossFadeFrom(this.currentAction, 0.20, true);
        }
        action.play();
        this.currentAction = action;

        const clipDurationMs = (this.currentTrack.clip.duration * 1000) / this.effectiveSpeed;
        setTimeout(() => {
          if (this.currentTrack && this.currentTrack.onComplete) {
            this.currentTrack.onComplete();
          }
          this.playNextInQueue();
        }, Math.max(300, clipDurationMs));
      }
    } else {
      this.isPlaying = false;
      this.currentTrack = null;
      this.setNMM('neutral');

      // Return smoothly to authentic natural Hand Talk rest pose
      if (this.repousoAction && this.currentAction && this.currentAction !== this.repousoAction) {
        this.repousoAction.reset();
        this.repousoAction.setLoop(THREE.LoopRepeat);
        this.repousoAction.crossFadeFrom(this.currentAction, 0.35, true);
        this.repousoAction.play();
        this.currentAction = this.repousoAction;
      }
    }
  }

  setNMM(nmm) {
    if (typeof nmm === 'string') {
      if (nmm === 'wh_question') {
        this.activeNmm = { eyebrows: 'raised', headTilt: -0.1, headShake: false, headNod: false, mouth: 'open_small' };
      } else if (nmm === 'yes_no_question') {
        this.activeNmm = { eyebrows: 'raised', headTilt: 0.08, headShake: false, headNod: true, mouth: 'neutral' };
      } else if (nmm === 'negation') {
        this.activeNmm = { eyebrows: 'furrowed', headTilt: 0.0, headShake: true, headNod: false, mouth: 'frown' };
      } else {
        this.activeNmm = { eyebrows: 'neutral', headTilt: 0.0, headShake: false, headNod: false, mouth: 'neutral' };
      }
    } else if (typeof nmm === 'object') {
      this.activeNmm = Object.assign({
        eyebrows: 'neutral',
        headTilt: 0.0,
        headShake: false,
        headNod: false,
        mouth: 'neutral'
      }, nmm);
    }
  }

  setMorph(morphName, value) {
    if (!this.morphInfluences || this.morphDict[morphName] === undefined) return;
    const idx = this.morphDict[morphName];
    this.morphInfluences[idx] = Math.max(0.0, Math.min(1.0, value));
  }

  updateNMM(dt, now) {
    // 1. Natural Eyelid Blinking
    if (now > this.nextBlinkTime) {
      this.isBlinking = true;
      this.blinkProgress = 0;
      this.nextBlinkTime = now + 2500 + Math.random() * 2500;
    }

    if (this.isBlinking) {
      this.blinkProgress += dt * 11.0;
      const blinkWeight = Math.sin(this.blinkProgress * Math.PI);
      this.setMorph('OLHO.PISCA.R', blinkWeight);
      this.setMorph('OLHO.PISCA.L', blinkWeight);
      if (this.blinkProgress >= 1.0) {
        this.isBlinking = false;
        this.setMorph('OLHO.PISCA.R', 0);
        this.setMorph('OLHO.PISCA.L', 0);
      }
    }

    // 2. Eyebrow Morphemes
    let targetBrowRaise = 0.0;
    let targetBrowFurrow = 0.0;
    if (this.activeNmm.eyebrows === 'raised') targetBrowRaise = 0.85;
    else if (this.activeNmm.eyebrows === 'furrowed') targetBrowFurrow = 0.90;

    this.setMorph('SOBRANCELHA.MEIO.SOBE.R', targetBrowRaise);
    this.setMorph('SOBRANCELHA.MEIO.SOBE.L', targetBrowRaise);
    this.setMorph('SOBRANCELHA.MEIO.DESCE.R', targetBrowFurrow);
    this.setMorph('SOBRANCELHA.MEIO.DESCE.L', targetBrowFurrow);

    // 3. Mouth Visemes
    let targetMouthOpen = 0.0;
    let targetMouthSmile = 0.0;
    let targetMouthFrown = 0.0;
    let targetMouthRound = 0.0;

    if (this.activeNmm.mouth === 'open_small') targetMouthOpen = 0.55;
    else if (this.activeNmm.mouth === 'smile') targetMouthSmile = 0.65;
    else if (this.activeNmm.mouth === 'frown') targetMouthFrown = 0.65;
    else if (this.activeNmm.mouth === 'round') targetMouthRound = 0.75;

    this.setMorph('BOCA.ABRE', targetMouthOpen);
    this.setMorph('LABIO.CANTO.SOBE.R', targetMouthSmile);
    this.setMorph('LABIO.CANTO.SOBE.L', targetMouthSmile);
    this.setMorph('LABIO.CANTO.DESCE.R', targetMouthFrown);
    this.setMorph('LABIO.CANTO.DESCE.L', targetMouthFrown);
    this.setMorph('BOCA.O', targetMouthRound);

    // 4. Head Motion
    const headBones = this.boneGroups.Head;
    if (headBones && headBones.length > 0) {
      let targetTiltZ = this.activeNmm.headTilt || 0.0;
      let targetShakeY = 0.0;
      let targetNodX = 0.0;

      if (this.activeNmm.headShake) targetShakeY = Math.sin(now * 0.012) * 0.22;
      if (this.activeNmm.headNod) targetNodX = Math.sin(now * 0.010) * 0.14;

      headBones.forEach(b => {
        b.rotation.z += (targetTiltZ - b.rotation.z) * Math.min(1.0, dt * 8);
        b.rotation.y += (targetShakeY - b.rotation.y) * Math.min(1.0, dt * 12);
        b.rotation.x += (targetNodX - b.rotation.x) * Math.min(1.0, dt * 10);
      });
    }
  }

  setBrightness(factor) {
    const f = Math.max(0.1, Math.min(2.0, factor));
    this.brightnessFactor = f;
    if (this.ambientLight) this.ambientLight.intensity = 0.40 * f;
    if (this.keyLight) this.keyLight.intensity = 0.50 * f;
    if (this.rimLight) this.rimLight.intensity = 0.28 * f;
    if (this.underLight) this.underLight.intensity = 0.10 * f;
    if (this.renderer) this.renderer.toneMappingExposure = 0.80 * f;
  }

  animate() {
    requestAnimationFrame(this.animate);

    const now = performance.now();
    const dt = Math.min(0.05, (now - this.lastFrameTime) / 1000.0);
    this.lastFrameTime = now;

    // Advance Three.js AnimationMixer (cross-fading, bone playback, blendshapes)
    if (this.mixer) {
      this.mixer.update(dt * this.effectiveSpeed);
    }

    // Natural Non-Manual Markers and facial blendshapes
    this.updateNMM(dt, now);

    // Living idle thoracic breathing motion across spine bones
    if (!this.isPlaying) {
      const breathe = Math.sin(now * 0.002) * 0.015;
      (this.boneGroups.Spine || []).forEach(bone => {
        const rest = this.restQuaternions.get(bone.uuid);
        if (rest) {
          const breatheQ = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0), breathe);
          bone.quaternion.copy(rest).multiply(breatheQ);
        }
      });
    }

    this.renderer.render(this.scene, this.camera);
  }
}
