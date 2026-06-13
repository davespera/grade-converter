import { client } from '$lib/api/client'
//Page Server and not just Page because private env variables are imported in '$lib/api/client' 
import type { Actions, PageServerLoad } from './$types'; 
import type { RequestEvent } from '@sveltejs/kit';

const PAGE_SIZE = 20;

export const load: PageServerLoad = async () => {
	const { data, error } = await client.GET('/scales/', {
		params: {
			query: { skip: 0, limit: PAGE_SIZE }
		}
	});

	if (error || !data) {
		return { status: 500, error };
	}

	return { scales: data, pageSize: PAGE_SIZE };
}

export const actions: Actions = {
	deleteScale: async ({ request }: RequestEvent) => {
		const data = await request.formData();
		const scaleId = Number(data.get('scale_id'));
		if (!Number.isFinite(scaleId)) {
			return { error: 'Invalid scale id.' };
		}

		const { error } = await client.DELETE('/scales/{scale_id}', {
			params: { path: { scale_id: scaleId } }
		});

		if (error) {
			return { error: 'Failed to delete scale.' };
		}

		return { success: `Deleted scale ${scaleId}.` };
	},
	deleteEquivalence: async ({ request }: RequestEvent) => {
		const data = await request.formData();
		const scaleId = Number(data.get('scale_id'));
		const equivalenceId = Number(data.get('equivalence_id'));
		if (!Number.isFinite(scaleId) || !Number.isFinite(equivalenceId)) {
			return { error: 'Invalid equivalence selection.' };
		}

		const { error } = await client.DELETE('/scales/{scale_id}/equivalences/{equivalence_id}', {
			params: {
				path: {
					scale_id: scaleId,
					equivalence_id: equivalenceId
				}
			}
		});

		if (error) {
			return { error: 'Failed to delete equivalence.' };
		}

		return { success: 'Deleted equivalence.' };
	},
	bulkDelete: async ({ request }: RequestEvent) => {
		const data = await request.formData();
		const scaleIds = new Set<number>();
		for (const value of data.getAll('scale_ids')) {
			const scaleId = Number(value);
			if (Number.isFinite(scaleId)) {
				scaleIds.add(scaleId);
			}
		}

		const equivalenceEntries = data.getAll('equivalence_ids') as string[];
		const equivalenceMap = new Map<string, { scaleId: number; equivalenceId: number }>();
		for (const entry of equivalenceEntries) {
			const [scaleIdRaw, equivalenceIdRaw] = entry.split(':');
			const scaleId = Number(scaleIdRaw);
			const equivalenceId = Number(equivalenceIdRaw);
			if (!Number.isFinite(scaleId) || !Number.isFinite(equivalenceId)) {
				continue;
			}
			if (scaleIds.has(scaleId)) {
				continue;
			}
			equivalenceMap.set(`${scaleId}:${equivalenceId}`, { scaleId, equivalenceId });
		}

		if (scaleIds.size === 0 && equivalenceMap.size === 0) {
			return { error: 'Select at least one scale or equivalence.' };
		}

		const scaleDeletes = Array.from(scaleIds).map((scaleId) =>
			client.DELETE('/scales/{scale_id}', {
				params: { path: { scale_id: scaleId } }
			})
		);
		const equivalenceDeletes = Array.from(equivalenceMap.values()).map((item) =>
			client.DELETE('/scales/{scale_id}/equivalences/{equivalence_id}', {
				params: {
					path: {
						scale_id: item.scaleId,
						equivalence_id: item.equivalenceId
					}
				}
			})
		);

		const results = await Promise.all([...scaleDeletes, ...equivalenceDeletes]);
		const hasError = results.some((result) => result.error);
		if (hasError) {
			return { error: 'Failed to delete some items.' };
		}

		return {
			success: `Deleted ${scaleIds.size} scale${scaleIds.size === 1 ? '' : 's'} and ${equivalenceMap.size} equivalence${equivalenceMap.size === 1 ? '' : 's'}.`
		};
	}
};