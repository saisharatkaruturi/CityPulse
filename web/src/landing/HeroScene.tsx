// WebGL hero scene (three.js), loaded only on the landing page. A low-poly city block: one building cluster
// per issue family around a central desk; glowing pulses ("reports") leave each family's beacon and travel the
// streets into the desk; cars loop the roads; a map pin floats over the electrical block. Decorative only —
// the page text carries the meaning. Pauses off-screen and in hidden tabs, renders one still frame under
// reduced motion, and disposes every GPU resource on unmount.
import { useEffect, useRef } from 'react';
import * as THREE from 'three';

type Fam = 'roads' | 'water' | 'lighting' | 'sanitation' | 'electrical' | 'drainage';

const COLORS: Record<Fam, number> = {
  roads: 0xc9d3e6, water: 0x8ec1ff, lighting: 0xf6dd6a, sanitation: 0x86ddb6, electrical: 0xff9b86, drainage: 0x8fdcd8,
};
// Block centres on a 3x3 grid (the middle cell is the desk). Streets run along x = ±3.5 and z = ±3.5.
const BLOCKS: { fam: Fam; x: number; z: number }[] = [
  { fam: 'roads', x: -7, z: -7 }, { fam: 'electrical', x: 0, z: -7 }, { fam: 'water', x: 7, z: -7 },
  { fam: 'sanitation', x: -7, z: 7 }, { fam: 'drainage', x: 0, z: 7 }, { fam: 'lighting', x: 7, z: 7 },
];

/** Deterministic pseudo-random, so the city is the same on every visit. */
function rng(seed: number) {
  let s = seed;
  return () => ((s = (s * 16807) % 2147483647) / 2147483647);
}

/** Street-following path from a beacon at (x, bz) to the desk's edge: out to the street, along it, in to the desk. */
function routeFor(x: number, bz: number): THREE.CurvePath<THREE.Vector3> {
  const y = 0.55;
  const s = Math.sign(bz) * 3.5;
  const sx = x > 0 ? 3.5 : x < 0 ? -3.5 : 3.5;
  const pts = [
    new THREE.Vector3(x, y, bz), new THREE.Vector3(x, y, s), new THREE.Vector3(sx, y, s),
    new THREE.Vector3(sx, y, 0), new THREE.Vector3(Math.sign(sx) * 1.3, y, 0),
  ];
  const path = new THREE.CurvePath<THREE.Vector3>();
  for (let i = 0; i < pts.length - 1; i++) if (!pts[i].equals(pts[i + 1])) path.add(new THREE.LineCurve3(pts[i], pts[i + 1]));
  return path;
}

export function supportsWebGL(): boolean {
  try {
    const c = document.createElement('canvas');
    return Boolean(c.getContext('webgl2') || c.getContext('webgl'));
  } catch {
    return false;
  }
}

export default function HeroScene({ onFail }: { onFail: () => void }) {
  const host = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = host.current;
    if (!el) return;
    const still = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    let renderer: THREE.WebGLRenderer;
    try {
      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'low-power' });
    } catch {
      onFail();
      return;
    }
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 0.98;
    el.appendChild(renderer.domElement);
    renderer.domElement.setAttribute('aria-hidden', 'true');

    const scene = new THREE.Scene();
    const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.1, 200);
    const camBase = new THREE.Vector3(26, 24, 26);
    camera.position.copy(camBase);
    camera.lookAt(0, 0, 0);

    // light: soft sky fill + one warm sun with soft shadows
    scene.add(new THREE.HemisphereLight(0xe6f0ff, 0xf3e3cc, 0.95));
    const sun = new THREE.DirectionalLight(0xfff1dc, 2.1);
    sun.position.set(14, 26, 10);
    sun.castShadow = true;
    sun.shadow.mapSize.set(1024, 1024);
    Object.assign(sun.shadow.camera, { left: -16, right: 16, top: 16, bottom: -16, near: 1, far: 70 });
    sun.shadow.radius = 4;
    scene.add(sun);

    const disposables: { dispose: () => void }[] = [];
    const mat = (color: number, opts: Partial<THREE.MeshStandardMaterialParameters> = {}) => {
      const m = new THREE.MeshStandardMaterial({ color, roughness: 0.62, metalness: 0.04, ...opts });
      disposables.push(m);
      return m;
    };
    const geo = <T extends THREE.BufferGeometry>(g: T) => { disposables.push(g); return g; };
    const box = geo(new THREE.BoxGeometry(1, 1, 1));

    const city = new THREE.Group();
    scene.add(city);

    // platform with a rounded feel: a slab and a thinner lip
    const slab = new THREE.Mesh(geo(new THREE.BoxGeometry(22, 0.8, 22)), mat(0xfbfaf7));
    slab.position.y = -0.4; slab.receiveShadow = true; city.add(slab);
    const lip = new THREE.Mesh(geo(new THREE.BoxGeometry(22.6, 0.5, 22.6)), mat(0x1b2840));
    lip.position.y = -0.95; city.add(lip);

    // streets and lane dashes
    const roadMat = mat(0x3a4660, { roughness: 0.9 });
    const dashMat = mat(0xffb340, { emissive: 0xffa020, emissiveIntensity: 0.35 });
    for (const p of [-3.5, 3.5]) {
      const h = new THREE.Mesh(box, roadMat); h.scale.set(22, 0.06, 1.6); h.position.set(0, 0.03, p); h.receiveShadow = true; city.add(h);
      const v = new THREE.Mesh(box, roadMat); v.scale.set(1.6, 0.061, 22); v.position.set(p, 0.03, 0); v.receiveShadow = true; city.add(v);
      for (let i = -10; i <= 10; i += 1.6) {
        const d1 = new THREE.Mesh(box, dashMat); d1.scale.set(0.7, 0.07, 0.12); d1.position.set(i, 0.05, p); city.add(d1);
        const d2 = new THREE.Mesh(box, dashMat); d2.scale.set(0.12, 0.071, 0.7); d2.position.set(p, 0.05, i); city.add(d2);
      }
    }

    // buildings per family, trees between them
    const r = rng(42);
    const treeTop = geo(new THREE.IcosahedronGeometry(0.42, 0));
    const treeTrunk = geo(new THREE.CylinderGeometry(0.07, 0.09, 0.4, 6));
    const leaf = mat(0x5fb98a, { flatShading: true });
    const trunk = mat(0x8a6a4a);
    const beacons: { fam: Fam; core: THREE.Mesh; halo: THREE.Mesh; x: number; z: number }[] = [];
    const haloGeo = geo(new THREE.RingGeometry(0.55, 0.75, 32));
    const coreGeo = geo(new THREE.SphereGeometry(0.28, 20, 16));
    for (const b of BLOCKS) {
      const base = COLORS[b.fam];
      const m = mat(base);
      const dark = mat(new THREE.Color(base).multiplyScalar(0.82).getHex());
      const count = 3;
      for (let i = 0; i < count; i++) {
        const w = 1.4 + r() * 1.3;
        const d = 1.4 + r() * 1.3;
        const h = 1.2 + r() * (b.fam === 'electrical' ? 4.4 : 3.2);
        const mesh = new THREE.Mesh(box, i === 0 ? m : dark);
        mesh.scale.set(w, h, d);
        mesh.position.set(b.x + (i - 1) * 1.9 + (r() - 0.5) * 0.4, h / 2, b.z + (r() - 0.5) * 2.2);
        mesh.castShadow = true; mesh.receiveShadow = true;
        city.add(mesh);
        // a roof cap in white for a crisp silhouette
        const cap = new THREE.Mesh(box, mat(0xffffff));
        cap.scale.set(w * 0.98, 0.08, d * 0.98); cap.position.set(mesh.position.x, h + 0.04, mesh.position.z);
        city.add(cap);
      }
      for (let i = 0; i < 2; i++) {
        const tx = b.x + (r() - 0.5) * 4.6, tz = b.z + (Math.sign(b.z) * -1.9);
        const t1 = new THREE.Mesh(treeTrunk, trunk); t1.position.set(tx, 0.2, tz); t1.castShadow = true; city.add(t1);
        const t2 = new THREE.Mesh(treeTop, leaf); t2.position.set(tx, 0.68, tz); t2.castShadow = true; city.add(t2);
      }
      // beacon on the street side of the block
      const bz = b.z - Math.sign(b.z) * 2.6;
      const cmat = new THREE.MeshStandardMaterial({ color: base, emissive: base, emissiveIntensity: 1.4 }); disposables.push(cmat);
      const core = new THREE.Mesh(coreGeo, cmat); core.position.set(b.x, 0.5, bz); city.add(core);
      const hmat = new THREE.MeshBasicMaterial({ color: base, transparent: true, opacity: 0.55, side: THREE.DoubleSide }); disposables.push(hmat);
      const halo = new THREE.Mesh(haloGeo, hmat); halo.rotation.x = -Math.PI / 2; halo.position.set(b.x, 0.08, bz); city.add(halo);
      beacons.push({ fam: b.fam, core, halo, x: b.x, z: bz });
    }

    // the desk: a dark tower with a glowing marigold crown
    const desk = new THREE.Mesh(box, mat(0x0d1626, { roughness: 0.35, metalness: 0.3 }));
    desk.scale.set(2.4, 3.6, 2.4); desk.position.set(0, 1.8, 0); desk.castShadow = true; city.add(desk);
    const crownMat = mat(0xffb340, { emissive: 0xff9a1a, emissiveIntensity: 0.9 });
    const crown = new THREE.Mesh(box, crownMat); crown.scale.set(2.5, 0.35, 2.5); crown.position.set(0, 3.78, 0); city.add(crown);
    const deskGlow = new THREE.PointLight(0xffa531, 6, 9, 2); deskGlow.position.set(0, 4.6, 0); city.add(deskGlow);

    // the floating pin over the electrical block
    const pin = new THREE.Group();
    const pinMat = mat(0xffb340, { emissive: 0xff8a00, emissiveIntensity: 0.25, roughness: 0.4 });
    const head = new THREE.Mesh(geo(new THREE.SphereGeometry(0.9, 28, 20)), pinMat);
    const tip = new THREE.Mesh(geo(new THREE.ConeGeometry(0.62, 1.5, 28)), pinMat);
    tip.rotation.x = Math.PI; tip.position.y = -1.05;
    const dot = new THREE.Mesh(geo(new THREE.SphereGeometry(0.34, 20, 16)), mat(0x0d1626));
    dot.position.set(0, 0.06, 0.66);
    head.castShadow = tip.castShadow = true;
    pin.add(head, tip, dot);
    pin.position.set(0, 8.2, -7);
    pin.scale.setScalar(1.35);
    city.add(pin);

    // pulses: one per family, travelling its route into the desk
    const pulseGeo = geo(new THREE.SphereGeometry(0.22, 16, 12));
    const pulses = beacons.map((b, i) => {
      const curve = routeFor(b.x, b.z);
      const pm = new THREE.MeshBasicMaterial({ color: COLORS[b.fam] }); disposables.push(pm);
      const mesh = new THREE.Mesh(pulseGeo, pm); city.add(mesh);
      const trailMat = new THREE.MeshBasicMaterial({ color: COLORS[b.fam], transparent: true, opacity: 0.35 }); disposables.push(trailMat);
      const trail = new THREE.Mesh(pulseGeo, trailMat); trail.scale.setScalar(1.7); city.add(trail);
      return { curve, mesh, trail, offset: i / beacons.length };
    });

    // cars looping the streets
    const carGeo = geo(new THREE.BoxGeometry(0.9, 0.45, 0.5));
    const carColors = [0xffffff, 0x1f63d1, 0xff9b86, 0x0d1626, 0x86ddb6];
    const cars = Array.from({ length: 7 }, (_, i) => {
      const m = new THREE.Mesh(carGeo, mat(carColors[i % carColors.length], { roughness: 0.3, metalness: 0.2 }));
      m.castShadow = true; city.add(m);
      const horizontal = i % 2 === 0;
      return { m, horizontal, lane: (i % 4 < 2 ? -3.5 : 3.5) + (i % 3 === 0 ? 0.35 : -0.35), speed: 0.045 + (i % 3) * 0.012, t: i * 3.1, dir: i % 3 === 0 ? -1 : 1 };
    });

    // sizing: keep the whole platform in frame at any aspect ratio
    const resize = () => {
      const w = el.clientWidth || 1, h = el.clientHeight || 1;
      renderer.setSize(w, h, false);
      const aspect = w / h;
      const view = 12.2;
      camera.left = -view * aspect; camera.right = view * aspect; camera.top = view; camera.bottom = -view;
      camera.zoom = aspect < 1 ? aspect * 1.05 : 1;
      camera.updateProjectionMatrix();
    };
    resize();
    const ro = new ResizeObserver(resize);
    ro.observe(el);

    // pointer parallax, eased
    const target = { x: 0, y: 0 };
    const current = { x: 0, y: 0 };
    const fine = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
    const onMove = (e: PointerEvent) => {
      target.x = (e.clientX / window.innerWidth - 0.5) * 2;
      target.y = (e.clientY / window.innerHeight - 0.5) * 2;
    };
    if (fine && !still) window.addEventListener('pointermove', onMove, { passive: true });

    const clock = new THREE.Clock();
    let frame = 0;
    let visible = true;
    const tick = () => {
      const t = clock.getElapsedTime();
      current.x += (target.x - current.x) * 0.04;
      current.y += (target.y - current.y) * 0.04;
      const ang = 0.12 * Math.sin(t * 0.12) + current.x * 0.12;
      camera.position.set(
        camBase.x * Math.cos(ang) - camBase.z * Math.sin(ang),
        camBase.y - current.y * 3,
        camBase.x * Math.sin(ang) + camBase.z * Math.cos(ang),
      );
      camera.lookAt(0, 1, 0);
      beacons.forEach((b, i) => {
        const p = (t * 0.6 + i * 0.37) % 1;
        b.halo.scale.setScalar(1 + p * 1.6);
        (b.halo.material as THREE.MeshBasicMaterial).opacity = 0.6 * (1 - p);
        b.core.scale.setScalar(1 + 0.12 * Math.sin(t * 3 + i));
      });
      pulses.forEach((p) => {
        const u = (t * 0.16 + p.offset) % 1;
        p.mesh.position.copy(p.curve.getPointAt(u));
        p.trail.position.copy(p.curve.getPointAt(Math.max(0, u - 0.035)));
        const fade = u > 0.92 ? (1 - u) / 0.08 : 1;
        p.mesh.scale.setScalar(fade);
        p.trail.scale.setScalar(1.7 * fade);
      });
      cars.forEach((c) => {
        c.t += c.speed * c.dir;
        const pos = ((c.t % 22) + 22) % 22 - 11;
        if (c.horizontal) { c.m.position.set(pos, 0.3, c.lane); c.m.rotation.y = 0; }
        else { c.m.position.set(c.lane, 0.3, pos); c.m.rotation.y = Math.PI / 2; }
      });
      pin.position.y = 8.2 + Math.sin(t * 1.6) * 0.45;
      pin.rotation.y = Math.sin(t * 0.7) * 0.5;
      crownMat.emissiveIntensity = 0.75 + 0.35 * Math.sin(t * 2.2);
      renderer.render(scene, camera);
    };

    const loop = () => {
      if (!visible || document.hidden) { frame = 0; return; }
      tick();
      frame = requestAnimationFrame(loop);
    };
    const io = new IntersectionObserver(([e]) => {
      visible = e.isIntersecting;
      if (visible && !frame && !still) frame = requestAnimationFrame(loop);
    });
    io.observe(el);
    const onVis = () => { if (!document.hidden && visible && !frame && !still) frame = requestAnimationFrame(loop); };
    document.addEventListener('visibilitychange', onVis);

    if (still) tick(); // one composed still frame, no motion
    else frame = requestAnimationFrame(loop);
    el.classList.add('is-ready');

    const onLost = (e: Event) => { e.preventDefault(); onFail(); };
    renderer.domElement.addEventListener('webglcontextlost', onLost);

    return () => {
      cancelAnimationFrame(frame);
      io.disconnect();
      ro.disconnect();
      window.removeEventListener('pointermove', onMove);
      document.removeEventListener('visibilitychange', onVis);
      renderer.domElement.removeEventListener('webglcontextlost', onLost);
      disposables.forEach((d) => d.dispose());
      renderer.dispose();
      renderer.domElement.remove();
    };
  }, [onFail]);

  return <div className="hero-scene" ref={host} />;
}
