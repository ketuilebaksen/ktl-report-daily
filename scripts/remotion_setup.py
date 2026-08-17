#!/usr/bin/env python3
"""
remotion_setup.py — write the Remotion project into remotion/ and install it.

The motion-design layer lives here. Rather than scattering a dozen small
React files across the repo (and hoping every one of them lands in the right
folder), the whole project is carried inside this single file and written out
at render time. One file to place, nothing to misname.

Remotion renders each frame in a headless browser, so it is far slower than
ffmpeg — about 27x slower than real time on a two-core runner. That is why we
only ever render the OVERLAY through it: a few seconds of transparent graphics
that ffmpeg then composites over footage it cut itself. Rendering the whole
video this way would take hours.

Usage:
  python3 scripts/remotion_setup.py        # write files + npm install
Returns non-zero if the install fails, so the caller can fall back.
"""
import json, os, shutil, subprocess, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.join(BASE, "remotion")

FILES = {
 "package.json": "{\n  \"name\": \"ktl-remotion\",\n  \"private\": true,\n  \"version\": \"1.0.0\",\n  \"scripts\": { \"render\": \"remotion render\" },\n  \"dependencies\": {\n    \"@remotion/cli\": \"4.0.512\",\n    \"react\": \"19.0.0\",\n    \"react-dom\": \"19.0.0\",\n    \"remotion\": \"4.0.512\"\n  },\n  \"devDependencies\": { \"@types/react\": \"19.0.0\", \"typescript\": \"5.6.3\" }\n}\n",
 "tsconfig.json": "{\n  \"compilerOptions\": {\n    \"target\": \"ES2018\",\n    \"module\": \"ESNext\",\n    \"jsx\": \"react-jsx\",\n    \"strict\": true,\n    \"moduleResolution\": \"bundler\",\n    \"noEmit\": true,\n    \"esModuleInterop\": true,\n    \"skipLibCheck\": true,\n    \"lib\": [\"DOM\", \"ES2018\"]\n  },\n  \"include\": [\"src\", \"remotion.config.ts\"]\n}\n",
 "remotion.config.ts": "import { Config } from \"@remotion/cli/config\";\nConfig.setVideoImageFormat(\"png\");\nConfig.setPixelFormat(\"yuva420p\");\nConfig.setCodec(\"vp8\");\n",
 "src/index.ts": "import { registerRoot } from \"remotion\";\nimport { RemotionRoot } from \"./Root\";\nregisterRoot(RemotionRoot);\n",
 "src/Root.tsx": "import React from \"react\";\nimport { Composition } from \"remotion\";\nimport { HookPages } from \"./HookPages\";\n\nexport const RemotionRoot: React.FC = () => (\n  <>\n    <Composition\n      id=\"HookPages\"\n      component={HookPages}\n      durationInFrames={9 * 24}\n      fps={24}\n      width={1920}\n      height={1080}\n      defaultProps={{\n        pages: [{ text: \"THE SILENCE\", at: 0.3 }],\n        accent: [245, 132, 38] as [number, number, number],\n      }}\n    />\n  </>\n);\n",
 "src/HookPages.tsx": "import React from \"react\";\nimport {\n  AbsoluteFill, interpolate, spring, staticFile, useCurrentFrame,\n  useVideoConfig,\n} from \"remotion\";\n\nexport type Page = { text: string; at: number; hold?: number };\nexport type Props = {\n  pages: Page[];\n  accent: [number, number, number];\n  paper?: [number, number, number];\n  ink?: [number, number, number];\n};\n\nconst rgb = (c: [number, number, number]) => `rgb(${c[0]},${c[1]},${c[2]})`;\n\n/**\n * A Vox-style page: it does not slide, it ARRIVES. The spring overshoots a\n * little and settles, the card enters at an angle and straightens as it lands,\n * and it leaves faster than it came. That asymmetry is what makes motion feel\n * designed rather than tweened.\n */\nconst PageCard: React.FC<{ page: Page; index: number; accent: string;\n  paper: string; ink: string }> = ({ page, index, accent, paper, ink }) => {\n  const frame = useCurrentFrame();\n  const { fps, width, height } = useVideoConfig();\n\n  const start = Math.round(page.at * fps);\n  const hold = Math.round((page.hold ?? 1.25) * fps);\n  const local = frame - start;\n  if (local < -2 || local > hold + fps) return null;\n\n  const fromLeft = index % 2 === 0;\n  const enter = spring({\n    frame: local, fps,\n    config: { damping: 14, mass: 0.7, stiffness: 130 },\n  });\n  // the exit is a fast ease-out, not a spring — leaving should feel decisive\n  const exit = interpolate(local, [hold, hold + fps * 0.34], [0, 1],\n    { extrapolateLeft: \"clamp\", extrapolateRight: \"clamp\" });\n\n  const offscreen = width * 0.62;\n  const x = interpolate(enter, [0, 1], [fromLeft ? -offscreen : offscreen, 0])\n    + exit * (fromLeft ? -offscreen * 0.7 : offscreen * 0.7);\n  const rot = interpolate(enter, [0, 1], [fromLeft ? -7 : 7, 0]) + exit * 4;\n  const opacity = Math.min(enter * 1.4, 1) * (1 - exit);\n  const scale = interpolate(enter, [0, 1], [0.88, 1]);\n\n  // three lanes so two cards can share the screen without colliding\n  const lane = 0.22 + 0.19 * (index % 3);\n\n  return (\n    <AbsoluteFill style={{ justifyContent: \"flex-start\", alignItems: fromLeft ? \"flex-start\" : \"flex-end\" }}>\n      <div style={{\n        marginTop: height * lane,\n        marginLeft: fromLeft ? width * 0.07 : 0,\n        marginRight: fromLeft ? 0 : width * 0.07,\n        transform: `translateX(${x}px) rotate(${rot}deg) scale(${scale})`,\n        opacity,\n        display: \"flex\",\n        background: paper,\n        boxShadow: \"0 18px 60px rgba(0,0,0,0.55)\",\n        borderRadius: 4,\n        overflow: \"hidden\",\n        maxWidth: width * 0.62,\n      }}>\n        <div style={{ width: 18, background: accent }} />\n        <div style={{\n          padding: \"30px 52px 34px 44px\",\n          fontFamily: \"HookAnton\",\n          fontSize: 74,\n          lineHeight: 1.06,\n          color: ink,\n          letterSpacing: 0.5,\n          textTransform: \"uppercase\",\n          whiteSpace: \"pre-wrap\",\n        }}>{page.text}</div>\n      </div>\n    </AbsoluteFill>\n  );\n};\n\nexport const HookPages: React.FC<Props> = ({ pages, accent, paper, ink }) => (\n  <AbsoluteFill style={{ backgroundColor: \"transparent\" }}>\n    <style>{`@font-face{font-family:HookAnton;src:url('${staticFile(\"Anton-Regular.ttf\")}') format('truetype');font-display:block;}`}</style>\n    {pages.map((p, i) => (\n      <PageCard key={i} page={p} index={i} accent={rgb(accent)}\n        paper={rgb(paper ?? [246, 247, 250])} ink={rgb(ink ?? [12, 14, 22])} />\n    ))}\n  </AbsoluteFill>\n);\n"
}

def write():
    for rel, text in FILES.items():
        path = os.path.join(ROOT, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(text)
    # the font the cards are set in — reuse the one the rest of the pipeline
    # already ships rather than carrying a second copy in the repo
    pub = os.path.join(ROOT, "public")
    os.makedirs(pub, exist_ok=True)
    src = os.path.join(BASE, "assets", "Anton-Regular.ttf")
    if os.path.exists(src):
        shutil.copy(src, os.path.join(pub, "Anton-Regular.ttf"))
    else:
        raise FileNotFoundError("assets/Anton-Regular.ttf is missing")


def install():
    if os.path.isdir(os.path.join(ROOT, "node_modules", "remotion")):
        print("[remotion] already installed")
        return
    print("[remotion] npm install …", flush=True)
    subprocess.run(["npm", "install", "--no-audit", "--no-fund",
                    "--loglevel=error"], cwd=ROOT, check=True)


def main():
    write()
    install()
    print(f"[remotion] ready at {ROOT}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[remotion] setup failed ({e})")
        sys.exit(1)
