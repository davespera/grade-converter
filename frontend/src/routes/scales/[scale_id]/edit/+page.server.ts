import { client } from '$lib/api/client';
import type { components } from '$lib/api/schema';
import { redirect, type RequestEvent } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';

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
	updateScale: async ({ params, request }: RequestEvent) => {
		const scaleId = Number(params.scale_id);
		if (!Number.isFinite(scaleId)) {
			return { error: 'Invalid scale id.' };
		}

		const data = await request.formData();
		const countryName = String(data.get('country_name') ?? '').trim();
		const scaleDescription = String(data.get('scale_description') ?? '').trim();
		const totalGradesRaw = String(data.get('total_grades') ?? '').trim();

		if (!countryName || !scaleDescription) {
			return { error: 'Country name and scale description are required.' };
		}

		const totalGrades = totalGradesRaw ? Number(totalGradesRaw) : null;
		if (totalGradesRaw && !Number.isInteger(totalGrades)) {
			return { error: 'Total grades must be a whole number.' };
		}

		const payload: components['schemas']['AcademicScaleUpdate'] = {
			country_name: countryName,
			scale_description: scaleDescription,
			total_grades: totalGrades
		};

		const { error } = await client.PATCH('/scales/{scale_id}', {
			params: { path: { scale_id: scaleId } },
			body: payload
		});

		if (error) {
			return { error: 'Failed to update scale.' };
		}

		throw redirect(303, `/scales/${scaleId}`);
	}
};