#!/usr/bin/env python3
"""
Generate Stoic Backgammon hero images via FAL.ai
Board spec from author:
- Rectangle, ~16:9 aspect ratio.
- Four 6-point sub-boards, a central bar splitting the board in two halves.
- Bar width ≈ 1.5× the width of a single point.
- Points are triangles; base slightly wider than a checker diameter.
- Checkers: circles, ~1 inch diameter. Board ~16 inches wide.
- Points alternate contrasting colors; opposing points differ in color.
- Style: photorealistic, cinematic lighting, dramatic composition.
"""
import os, sys, json, time, pathlib, subprocess

FAL_KEY = os.environ.get("FAL_KEY", "").strip()
if not FAL_KEY:
    print("Error: Set FAL_KEY environment variable.")
    sys.exit(1)

OUT_DIR = pathlib.Path("/Users/prh/Developer/huffmanwrites/static/img/articles")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# aspect ratio -> FAL size mapping
SIZES = {
    "16x9": {"width": 1024, "height": 576},
    "4x5": {"width": 1024, "height": 1280},
}

BOARD_SPEC = (
    "A backgammon board is a rectangular wooden playing surface in 16:9 aspect ratio. "
    "It is divided into four 6-point quadrants by a central vertical bar. "
    "The bar is about 1.5 times the width of a single point. "
    "Points are narrow triangles with bases slightly wider than a checker; "
    "they alternate in two contrasting colors. "
    "Checkers are smooth circular discs about 1 inch in diameter, stacked neatly. "
    "The board is roughly 16 inches wide. "
    "Opposing points use different colors (e.g., warm tan vs cool slate). "
    "Razor-sharp focus, photorealistic textures, dramatic cinematic lighting, no text."
)

SECTIONS = [
    ("sb-the-roll", "A dramatic close-up of a player's hand releasing two precision dice onto a luxurious backgammon board. " + BOARD_SPEC),
    ("sb-interlude-1", "A serene still-life of a backgammon board mid-game at golden hour, soft light streaming across the checkers. " + BOARD_SPEC),
    ("sb-the-dichotomy", "A backgammon board split by a stark shaft of light—half illuminated, half in shadow—symbolizing duality. " + BOARD_SPEC),
    ("sb-the-anchor", "A low-angle cinematic shot focusing on a lone backgammon checker anchored on a point, shallow depth of field. " + BOARD_SPEC),
    ("sb-interlude-2", "An overhead view of a backgammon board with pieces scattered in a pattern resembling a constellation. " + BOARD_SPEC),
    ("sb-the-blitz", "Dynamic action shot of backgammon checkers being struck mid-game, pieces suspended in dramatic motion blur. " + BOARD_SPEC),
    ("sb-the-back-game", "A tense backgammon position with multiple checkers trapped behind a prime, cinematic lighting, high detail. " + BOARD_SPEC),
    ("sb-interlude-3", "A backgammon board half-covered by autumn leaves, warm afternoon light, peaceful contemplative mood. " + BOARD_SPEC),
    ("sb-the-prime", "A perfect wall of five backgammon checkers forming a prime, shot from table level with dramatic side-lighting. " + BOARD_SPEC),
    ("sb-the-hit", "Macro shot of one backgammon checker striking another, sending it to the bar—frozen motion, cinematic. " + BOARD_SPEC),
    ("sb-interlude-4", "A vintage backgammon set in a dimly lit study, leather and wood textures, moody chiaroscuro lighting. " + BOARD_SPEC),
    ("sb-the-race", "A backgammon board from high angle showing checkers sprinting toward home, dramatic perspective and lighting. " + BOARD_SPEC),
    ("sb-the-double", "Two identical backgammon dice showing double sixes resting on the lip of a wooden doubling cube. " + BOARD_SPEC),
    ("sb-the-bear-off", "Final moments of a backgammon game: the last checker being borne off the ace point, decisive cinematic framing. " + BOARD_SPEC),
]

def generate_image(prompt, width, height, seed=None):
    payload = {
        "prompt": prompt,
        "image_size": {"width": width, "height": height},
        "num_inference_steps": 28,
        "guidance_scale": 3.5,
        "num_images": 1,
        "enable_safety_checker": False,
    }
    if seed is not None:
        payload["seed"] = seed

    cmd = [
        "curl", "-s", "-X", "POST",
        "https://queue.fal.run/fal-ai/flux/dev",
        "-H", f"Authorization: Key {FAL_KEY}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"curl error: {result.stderr}")
        return None
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"Bad JSON: {result.stdout}")
        return None
    return data

def poll_status(request_id):
    while True:
        cmd = [
            "curl", "-s",
            f"https://queue.fal.run/fal-ai/flux/requests/{request_id}",
            "-H", f"Authorization: Key {FAL_KEY}",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)
        status = data.get("status", "unknown")
        if status == "COMPLETED":
            return data
        if status in ("FAILED", "ERROR"):
            print(f"Generation failed: {data}")
            return None
        time.sleep(2)

def download(url, dest):
    subprocess.run(["curl", "-sL", "-o", str(dest), url], check=True)

def main():
    for slug, base_prompt in SECTIONS:
        for ratio, dims in SIZES.items():
            dest = OUT_DIR / f"{slug} {ratio}.webp"
            if dest.exists():
                print(f"Skipping existing {dest.name}")
                continue

            print(f"Generating {slug} {ratio} ...", end=" ", flush=True)
            data = generate_image(base_prompt, dims["width"], dims["height"])
            if data is None:
                print("FAIL (req)")
                continue
            request_id = data.get("request_id")
            if not request_id:
                # immediate/edge-case
                images = data.get("images", [])
                if images:
                    download(images[0]["url"], dest)
                    print("OK")
                    continue
                print(f"FAIL (no request_id): {data}")
                continue
            result = poll_status(request_id)
            if result is None:
                print("FAIL (poll)")
                continue
            images = result.get("images", [])
            if not images:
                print("FAIL (no images)")
                continue
            download(images[0]["url"], dest)
            print("OK")
            time.sleep(0.5)

    print("\nDone.")

if __name__ == "__main__":
    main()
