import { client } from '$lib/api/client';
import type { Actions, PageServerLoad } from './$types';
import type { RequestEvent } from '@sveltejs/kit';
import { redirect } from '@sveltejs/kit';

export const load: PageServerLoad = async ({ params }) => {
	const scaleId = Number(params.scale_id);
	if (!Number.isFinite(scaleId)) {
		return { status: 400, error: 'Invalid scale id.' };
	}

	const { data, error } = await client.GET('/scales/{scale_id}', {
		params: { path: { scale_id: scaleId } }
	});

	if (error || !data) {
		return { status: 500, error };
	}

	return { scale: data };
};

export const actions: Actions = {
	deleteScale: async ({ params }: RequestEvent) => {
		const scaleId = Number(params.scale_id);
		if (!Number.isFinite(scaleId)) {
			return { error: 'Invalid scale id.' };
		}

		const { error } = await client.DELETE('/scales/{scale_id}', {
			params: { path: { scale_id: scaleId } }
		});

		if (error) {
			return { error: 'Failed to delete scale.' };
		}

		throw redirect(303, '/scales');
	},
	deleteEquivalence: async ({ params, request }: RequestEvent) => {
		const scaleId = Number(params.scale_id);
		const data = await request.formData();
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
	}
};
