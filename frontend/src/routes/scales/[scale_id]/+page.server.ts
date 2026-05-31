import { client } from '$lib/api/client';
import type { components } from '$lib/api/schema';
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
	},
	updateEquivalence: async ({ params, request }: RequestEvent) => {
		const scaleId = Number(params.scale_id);
		const data = await request.formData();
		const equivalenceId = Number(data.get('equivalence_id'));
		const originGrade = String(data.get('origin_grade') ?? '').trim();
		const spanish510Raw = String(data.get('spanish_5_10') ?? '').trim();
		const spanish14Raw = String(data.get('spanish_1_4') ?? '').trim();
		const spanishLiteralRaw = String(data.get('spanish_literal') ?? '').trim();

		if (!Number.isFinite(scaleId) || !Number.isFinite(equivalenceId)) {
			return { error: 'Invalid equivalence selection.' };
		}
		if (!originGrade || !spanish510Raw || !spanishLiteralRaw) {
			return { error: 'Origin grade, Spanish 5-10, and Spanish literal are required.' };
		}

		const spanish510 = Number(spanish510Raw);
		if (!Number.isFinite(spanish510)) {
			return { error: 'Spanish 5-10 must be a number.' };
		}

		const spanish14 = spanish14Raw ? Number.parseInt(spanish14Raw, 10) : null;
		if (spanish14 !== null && (!Number.isInteger(spanish14) || spanish14 < 1 || spanish14 > 4)) {
			return { error: 'Spanish 1-4 must be between 1 and 4.' };
		}

		const { data: updatedEquivalence, error } = await client.PATCH(
			'/scales/{scale_id}/equivalences/{equivalence_id}',
			{
				params: {
					path: {
						scale_id: scaleId,
						equivalence_id: equivalenceId
					}
				},
				body: {
					origin_grade: originGrade,
					spanish_5_10: spanish510,
					spanish_1_4: spanish14,
					spanish_literal: spanishLiteralRaw as components['schemas']['SpanishLiteralEnum']
				}
			}
		);

		if (error || !updatedEquivalence) {
			return { error: 'Failed to update equivalence.' };
		}

		return { success: `Updated ${updatedEquivalence.origin_grade} equivalence.` };
	}
};
