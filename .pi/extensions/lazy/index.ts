import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";

/**
 * Loads packages installed by Lazy Pi.
 *
 * @param pi Pi extension API.
 */
export default async function index(pi: ExtensionAPI): Promise<void> {
	const loaders = [

	];
	for (const load of loaders) {
		try {
			const module = await load();
			if (typeof module.default === "function") await module.default(pi);
		} catch (error) {
			console.error("Failed to load Lazy Pi package extension", error);
		}
	}
}
