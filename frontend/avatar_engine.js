/**
 * AvatarEngine: WebGL 3D Avatar built on Three.js.
 * Implements a procedural articulated humanoid skeleton with bone rigging,
 * Quaternion Spherical Linear Interpolation (SLERP) for coarticulation,
 * and Non-Manual Marker (NMM) facial blendshapes.
 */

class AvatarEngine {
  constructor(canvasElement) {
    this.canvas = canvasElement;
    this.playbackSpeed = 1.0;
    this.isPlaying = false;
    this.animationQueue = [];
    this.currentTrack = null;
    this.trackTime = 0;

    this.initScene();
    this.initAvatar();
    this.animate = this.animate.bind(this);
    requestAnimationFrame(this.animate);
  }

  initScene() {
    this.scene = new THREE.Scene();

    const width = this.canvas.clientWidth || 400;
    const height = this.canvas.clientHeight || 450;

    this.camera = new THREE.PerspectiveCamera(38, width / height, 0.1, 100);
    this.camera.position.set(0, 1.25, 2.2);
    this.camera.lookAt(0, 1.15, 0);

    this.renderer = new THREE.WebGLRenderer({
      canvas: this.canvas,
      alpha: true,
      antialias: true
    });
    this.renderer.setSize(width, height);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    // Studio Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.85);
    this.scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0x06b6d4, 1.2);
    dirLight.position.set(2, 4, 3);
    this.scene.add(dirLight);

    const rimLight = new THREE.DirectionalLight(0xa855f7, 0.8);
    rimLight.position.set(-2, 3, -2);
    this.scene.add(rimLight);

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

  initAvatar() {
    this.avatarGroup = new THREE.Group();
    this.scene.add(this.avatarGroup);

    // High quality materials
    this.skinMat = new THREE.MeshStandardMaterial({ color: 0xf5d0b5, roughness: 0.5 });
    this.clothesMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.4, metalness: 0.1 });
    this.accentMat = new THREE.MeshStandardMaterial({ color: 0x06b6d4, roughness: 0.3 });

    // Torso
    const torsoGeo = new THREE.CylinderGeometry(0.24, 0.2, 0.65, 16);
    this.torso = new THREE.Mesh(torsoGeo, this.clothesMat);
    this.torso.position.y = 0.9;
    this.avatarGroup.add(this.torso);

    // Neck & Head
    this.neck = new THREE.Group();
    this.neck.position.y = 0.35;
    this.torso.add(this.neck);

    const headGeo = new THREE.SphereGeometry(0.16, 24, 24);
    this.head = new THREE.Mesh(headGeo, this.skinMat);
    this.head.position.y = 0.22;
    this.neck.add(this.head);

    // Facial features (Eyes & Eyebrows for NMM)
    const eyeGeo = new THREE.SphereGeometry(0.022, 12, 12);
    const eyeMat = new THREE.MeshBasicMaterial({ color: 0x0f172a });

    this.leftEye = new THREE.Mesh(eyeGeo, eyeMat);
    this.leftEye.position.set(-0.06, 0.04, 0.14);
    this.head.add(this.leftEye);

    this.rightEye = new THREE.Mesh(eyeGeo, eyeMat);
    this.rightEye.position.set(0.06, 0.04, 0.14);
    this.head.add(this.rightEye);

    // Eyebrows (for interrogative NMM expressions)
    const browGeo = new THREE.BoxGeometry(0.05, 0.012, 0.01);
    const browMat = new THREE.MeshBasicMaterial({ color: 0x334155 });

    this.leftBrow = new THREE.Mesh(browGeo, browMat);
    this.leftBrow.position.set(-0.06, 0.08, 0.145);
    this.head.add(this.leftBrow);

    this.rightBrow = new THREE.Mesh(browGeo, browMat);
    this.rightBrow.position.set(0.06, 0.08, 0.145);
    this.head.add(this.rightBrow);

    // Limbs: Arm joints
    this.bones = {};

    // Right Arm
    this.bones.RightArm = new THREE.Group();
    this.bones.RightArm.position.set(0.26, 0.25, 0);
    this.torso.add(this.bones.RightArm);

    const rUpperArmMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.045, 0.28, 12), this.clothesMat);
    rUpperArmMesh.position.y = -0.14;
    this.bones.RightArm.add(rUpperArmMesh);

    this.bones.RightForeArm = new THREE.Group();
    this.bones.RightForeArm.position.y = -0.28;
    this.bones.RightArm.add(this.bones.RightForeArm);

    const rForeArmMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.04, 0.26, 12), this.skinMat);
    rForeArmMesh.position.y = -0.13;
    this.bones.RightForeArm.add(rForeArmMesh);

    this.bones.RightHand = new THREE.Group();
    this.bones.RightHand.position.y = -0.26;
    this.bones.RightForeArm.add(this.bones.RightHand);

    const rHandMesh = new THREE.Mesh(new THREE.BoxGeometry(0.07, 0.09, 0.025), this.skinMat);
    rHandMesh.position.y = -0.045;
    this.bones.RightHand.add(rHandMesh);

    // Left Arm
    this.bones.LeftArm = new THREE.Group();
    this.bones.LeftArm.position.set(-0.26, 0.25, 0);
    this.torso.add(this.bones.LeftArm);

    const lUpperArmMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.045, 0.28, 12), this.clothesMat);
    lUpperArmMesh.position.y = -0.14;
    this.bones.LeftArm.add(lUpperArmMesh);

    this.bones.LeftForeArm = new THREE.Group();
    this.bones.LeftForeArm.position.y = -0.28;
    this.bones.LeftArm.add(this.bones.LeftForeArm);

    const lForeArmMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.04, 0.26, 12), this.skinMat);
    lForeArmMesh.position.y = -0.13;
    this.bones.LeftForeArm.add(lForeArmMesh);

    this.bones.LeftHand = new THREE.Group();
    this.bones.LeftHand.position.y = -0.26;
    this.bones.LeftForeArm.add(this.bones.LeftHand);

    const lHandMesh = new THREE.Mesh(new THREE.BoxGeometry(0.07, 0.09, 0.025), this.skinMat);
    lHandMesh.position.y = -0.045;
    this.bones.LeftHand.add(lHandMesh);
  }

  setSpeed(speed) {
    this.playbackSpeed = Math.max(0.5, Math.min(2.0, speed));
  }

  playSequence(keyframesList, nmmExpression = 'neutral') {
    if (!keyframesList || keyframesList.length === 0) return;
    this.animationQueue.push({
      keyframes: keyframesList,
      nmm: nmmExpression,
      duration: keyframesList[keyframesList.length - 1].time || 1.0
    });

    if (!this.isPlaying) {
      this.playNextInQueue();
    }
  }

  playNextInQueue() {
    if (this.animationQueue.length === 0) {
      this.isPlaying = false;
      this.currentTrack = null;
      this.resetPose();
      return;
    }

    this.isPlaying = true;
    this.currentTrack = this.animationQueue.shift();
    this.trackTime = 0;
    this.applyNMM(this.currentTrack.nmm);
  }

  applyNMM(expression) {
    if (expression === 'question' || expression === 'furrow_brow') {
      this.leftBrow.position.y = 0.095;
      this.rightBrow.position.y = 0.095;
      this.neck.rotation.x = -0.08;
    } else if (expression === 'nod') {
      this.neck.rotation.x = 0.12;
    } else {
      this.leftBrow.position.y = 0.08;
      this.rightBrow.position.y = 0.08;
      this.neck.rotation.x = 0;
    }
  }

  resetPose() {
    // Smoothly return arms to relaxed rest pose
    for (const key of Object.keys(this.bones)) {
      this.bones[key].quaternion.slerp(new THREE.Quaternion(0, 0, 0, 1), 0.1);
    }
    this.applyNMM('neutral');
  }

  animate() {
    requestAnimationFrame(this.animate);

    if (this.isPlaying && this.currentTrack) {
      const dt = 0.016 * this.playbackSpeed;
      this.trackTime += dt;

      const frames = this.currentTrack.keyframes;
      // Find current bounding keyframes
      let f1 = frames[0];
      let f2 = frames[frames.length - 1];

      for (let i = 0; i < frames.length - 1; i++) {
        if (this.trackTime >= frames[i].time && this.trackTime <= frames[i + 1].time) {
          f1 = frames[i];
          f2 = frames[i + 1];
          break;
        }
      }

      const segmentSpan = (f2.time - f1.time) || 0.001;
      const alpha = Math.min(1.0, Math.max(0.0, (this.trackTime - f1.time) / segmentSpan));

      // Quaternion SLERP interpolation across skeletal bones
      for (const boneName of ['RightArm', 'RightForeArm', 'RightHand', 'LeftArm', 'LeftForeArm', 'LeftHand']) {
        if (f1[boneName] && f2[boneName] && this.bones[boneName]) {
          const q1 = new THREE.Quaternion(...f1[boneName]);
          const q2 = new THREE.Quaternion(...f2[boneName]);
          q1.slerp(q2, alpha);
          this.bones[boneName].quaternion.copy(q1);
        }
      }

      if (this.trackTime >= this.currentTrack.duration) {
        this.playNextInQueue();
      }
    }

    // Subtle idle breathing motion
    if (!this.isPlaying) {
      const breathe = Math.sin(Date.now() * 0.002) * 0.015;
      this.torso.position.y = 0.9 + breathe;
    }

    this.renderer.render(this.scene, this.camera);
  }
}
