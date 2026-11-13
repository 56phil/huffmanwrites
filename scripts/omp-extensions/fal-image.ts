import type { ExtensionAPI } from "@oh-my-pi/pi-coding-agent";
import { mkdtemp, writeFile } from "node:fs/promises";
import { homedir, tmpdir } from "node:os";
import { join } from "node:path";

// fal.ai-backed replacement for the built-in generate_image.
//
// Why this exists: the built-in tool resolves its model through the `image`
// model role, and this machine has no image-capable provider configured, so
// every call fails with "Image generation exhausted the resolved image chain".
// The only image credential here is fal.ai's FAL_KEY, and fal exposes no
// OpenAI-compatible /images/generations endpoint, so no models.yml entry can
// reach it. An extension tool registered under the same name takes precedence
// over the built-in one, which is what this module is.

type FalImage = { url: string; width?: number; height?: number; content_type?: string };

const QUEUE = "https://queue.fal.run";
const DEFAULT_MODEL = "fal-ai/flux/dev";
const TIMEOUT_MS = 3 * 60 * 1000;
const POLL_MS = 1500;

const ASPECT_TO_FAL: Record<string, string> = {
	"1:1": "square_hd",
	"16:9": "landscape_16_9",
	"4:3": "landscape_4_3",
	"3:2": "landscape_4_3",
	"3:4": "portrait_4_3",
	"2:3": "portrait_4_3",
	"9:16": "portrait_16_9",
};

async function readKey(pi: ExtensionAPI): Promise<string> {
	if (process.env.FAL_KEY) return process.env.FAL_KEY.trim();
	try {
		const secrets = await Bun.file(join(homedir(), ".secrets")).text();
		const match = secrets.match(/^\s*(?:export\s+)?FAL_KEY\s*=\s*["']?([^"'\s]+)/m);
		if (match) return match[1];
	} catch {
		// fall through to the keychain
	}
	const user = process.env.USER ?? "";
	const result = await pi.exec(
		"security",
		["find-generic-password", "-a", user, "-s", "huffmanwrites-fal", "-w"],
		{},
	);
	const value = result.stdout.trim();
	if (result.code !== 0 || !value) {
		throw new Error(
			"No fal.ai key: set FAL_KEY, add FAL_KEY to ~/.secrets, or store it as the keychain item huffmanwrites-fal.",
		);
	}
	return value;
}

async function sleep(ms: number, signal?: AbortSignal) {
	if (signal?.aborted) throw new Error("Image generation cancelled");
	const { promise, resolve, reject } = Promise.withResolvers<void>();
	const timer = setTimeout(() => {
		signal?.removeEventListener("abort", onAbort);
		resolve();
	}, ms);
	const onAbort = () => {
		clearTimeout(timer);
		reject(new Error("Image generation cancelled"));
	};
	signal?.addEventListener("abort", onAbort, { once: true });
	return promise;
}

export default function falImage(pi: ExtensionAPI) {
	const z = pi.zod;

	pi.registerTool({
		name: "generate_image",
		label: "Generate Image",
		description:
			"Generate or edit images through fal.ai and write them to temporary paths. " +
			"Returns the saved paths; open them with read. The default model is fal-ai/flux/dev; " +
			"pass model to select any fal text-to-image endpoint (e.g. fal-ai/flux/schnell, fal-ai/nano-banana-2).",
		parameters: z.object({
			subject: z.string().describe("Main image prompt. For edits, describe the result and each input image's role."),
			action: z.string().optional().describe("What the subject is doing."),
			scene: z.string().optional().describe("Location or environment."),
			composition: z.string().optional().describe("Camera angle and framing."),
			lighting: z.string().optional().describe("Lighting setup."),
			style: z.string().optional().describe("Artistic style."),
			text: z.string().optional().describe("Short text to render in the image, when legibility is required."),
			aspect_ratio: z
				.enum(["1:1", "3:4", "4:3", "9:16", "16:9", "3:2", "2:3"])
				.optional()
				.describe("Requested output aspect ratio."),
			width: z.number().optional().describe("Exact output width in pixels; requires height. Rounded up to a multiple of 16."),
			height: z.number().optional().describe("Exact output height in pixels; requires width. Rounded up to a multiple of 16."),
			model: z.string().optional().describe("fal endpoint id, e.g. fal-ai/flux/dev."),
			input: z
				.array(z.string())
				.optional()
				.describe("Local image paths to edit. One reference is supported on the generic image-to-image route."),
			seed: z.number().optional().describe("Fixed seed for a reproducible render."),
		}),

		async execute(_toolCallId, params, signal, _onUpdate, _ctx) {
			const endpoint = (params.model ?? DEFAULT_MODEL).replace(/^\/+/, "");
			const key = await readKey(pi);

			const parts = [params.subject, params.action, params.scene, params.composition, params.lighting, params.style]
				.filter((part): part is string => Boolean(part && part.trim()))
				.map(part => part.trim().replace(/\.$/, ""));
			if (params.text) parts.push(`Render the text: ${params.text}`);
			const prompt = parts.join(". ");

			const body: Record<string, unknown> = {
				prompt,
				num_images: 1,
				enable_safety_checker: false,
			};
			if (params.aspect_ratio) body.image_size = ASPECT_TO_FAL[params.aspect_ratio];
			if (params.width !== undefined || params.height !== undefined) {
				if (!params.width || !params.height) {
					throw new Error("width and height must be given together");
				}
				body.image_size = {
					width: Math.max(16, Math.round(params.width / 16) * 16),
					height: Math.max(16, Math.round(params.height / 16) * 16),
				};
			}
			if (typeof params.seed === "number") body.seed = params.seed;

			let url = `${QUEUE}/${endpoint}`;
			const references = params.input ?? [];
			if (references.length > 0) {
				if (references.length > 1) {
					throw new Error(`fal image edits accept one reference on this route; got ${references.length}`);
				}
				const path = references[0].replace(/^~/, homedir());
				const file = Bun.file(path);
				if (!(await file.exists())) throw new Error(`Input image not found: ${path}`);
				const bytes = Buffer.from(await file.arrayBuffer());
				const mime = file.type || "image/png";
				body.image_url = `data:${mime};base64,${bytes.toString("base64")}`;
				if (!body.image_size) body.image_size = "landscape_4_3";
				url = `${QUEUE}/${endpoint.replace(/\/text-to-image$/, "")}/image-to-image`;
			}

			const submit = await fetch(url, {
				method: "POST",
				headers: { Authorization: `Key ${key}`, "Content-Type": "application/json" },
				body: JSON.stringify(body),
				signal,
			});
			if (!submit.ok) {
				throw new Error(`fal submit failed: HTTP ${submit.status} ${(await submit.text()).slice(0, 400)}`);
			}
			const queued = (await submit.json()) as { status_url?: string; response_url?: string };
			if (!queued.status_url || !queued.response_url) {
				throw new Error(`fal submit returned no status/response URL: ${JSON.stringify(queued).slice(0, 300)}`);
			}

			const deadline = Date.now() + TIMEOUT_MS;
			let status = "IN_QUEUE";
			while (status !== "COMPLETED") {
				if (Date.now() > deadline) throw new Error("fal generation timed out after 3 minutes");
				await sleep(POLL_MS, signal);
				const poll = await fetch(queued.status_url, { headers: { Authorization: `Key ${key}` }, signal });
				if (!poll.ok) throw new Error(`fal status failed: HTTP ${poll.status}`);
				const state = (await poll.json()) as { status?: string; error?: string };
				status = state.status ?? "IN_QUEUE";
				if (status === "FAILED" || state.error) {
					throw new Error(`fal generation failed: ${state.error ?? "unknown error"}`);
				}
			}

			const result = await fetch(queued.response_url, { headers: { Authorization: `Key ${key}` }, signal });
			if (!result.ok) throw new Error(`fal result failed: HTTP ${result.status}`);
			const payload = (await result.json()) as { images?: FalImage[] };
			const images = payload.images ?? [];
			if (images.length === 0) return { content: [{ type: "text", text: "No image data returned." }], details: { imageCount: 0 } };

			const dir = await mkdtemp(join(tmpdir(), "omp-image-"));
			const paths: string[] = [];
			for (const [index, image] of images.entries()) {
				const download = await fetch(image.url, { signal });
				if (!download.ok) throw new Error(`fal image download failed: HTTP ${download.status}`);
				const ext = (image.content_type ?? "image/png").split("/")[1]?.replace("jpeg", "jpg") ?? "png";
				const target = join(dir, `omp-image-${Date.now()}-${index}.${ext}`);
				await writeFile(target, Buffer.from(await download.arrayBuffer()));
				paths.push(target);
			}

			const sizes = images.map(image => (image.width && image.height ? ` (${image.width}x${image.height})` : ""));
			return {
				content: [
					{
						type: "text",
						text: `Provider: fal.ai, model: ${endpoint}\nSaved ${paths.length} image(s):\n${paths
							.map((path, index) => `${path}${sizes[index]}`)
							.join("\n")}`,
					},
				],
				details: { provider: "fal", model: endpoint, imageCount: paths.length, imagePaths: paths },
			};
		},
	});
}
