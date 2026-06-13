import { client } from '$lib/api/client';
// Page Server (not just Page) because '$lib/api/client' imports private env vars.
import type { PageServerLoad } from './$types';

const RESULT_LIMIT = 50;

export const load: PageServerLoad = async ({ url }) => {
	const country = url.searchParams.get('country')?.trim() ?? '';
	const scale = url.searchParams.get('scale')?.trim() ?? '';

	// No query yet: render the empty search prompt without hitting the API.
	if (!country && !scale) {
		return { country, scale, results: null };
	}

	const { data, error } = await client.GET('/scales/search', {
		params: {
			query: {
				country: country || undefined,
				scale_description: scale || undefined,
				limit: RESULT_LIMIT
			}
		}
	});

	if (error || !data) {
		return { country, scale, results: [], error: true };
	}

	return { country, scale, results: data };
};
