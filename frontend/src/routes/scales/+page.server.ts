import { client } from '$lib/api/client'
import type { components } from '$lib/api/schema';
//Page Server and not just Page because private env variables are imported in '$lib/api/client' 
import type { PageServerLoad } from './$types'; 

export const load: PageServerLoad = async () => {
	const { data, error } = await client.GET('/scales/', {
		params: {
			query: { limit: 50, page: 1}
		}
	});

	if (error || !data) {
		return { status: 500, error };
	}
	
	return { scales: data };
}

export const actions = {
	createScale: async ({ request }) => {
		const data = await request.formData();
		const country_name = data.get('countryName') as string;
		const scale_description = data.get('scaleDescription') as string;
		const total_grades = data.get('totalGrades') ? Number(data.get('totalGrades')) : null; // NOTE: In the future utomatically generate this value


		const origin_grades = data.getAll('originGrade') as string[];
		const spanish_5_10s = data.getAll('spanish_5_10') as string[];
		const spanish_1_4s = data.getAll('spanish_1_4') as string[];
		const spanish_literals = data.getAll('spanishLiteral') as string[];

		const equivalences = origin_grades.map((origin_grade, index) => {
			const span_1_4_val = spanish_1_4s[index].trim();
			return {
				origin_grade: origin_grade.trim(),
				spanish_5_10: Number(spanish_5_10s[index].trim()),
				spanish_1_4: span_1_4_val ? parseInt(span_1_4_val, 10) : null,
				spanish_literal: spanish_literals[index].trim() as components['schemas']['SpanishLiteralEnum'],
			};
		});

		const { data: scaleData, error: scaleError } = await client.POST("/scales/", {
			body: {
				country_name: country_name,
				scale_description: scale_description,
				total_grades: total_grades,
			}
		});

		if (scaleError || !scaleData) {
			return { status: 500, error: scaleError };
		}

		const scale_id = scaleData.id;

		const results = await Promise.all(
			equivalences.map(eq =>
				client.POST("/scales/{scale_id}/equivalences/", {
					params: {
						path: { scale_id: scale_id }
					},
					body: {
						origin_grade: eq.origin_grade, 
						spanish_5_10: eq.spanish_5_10,
						spanish_1_4: eq.spanish_1_4,
						spanish_literal: eq.spanish_literal,
					} 
				})
			)
		);

		const hasError = results.some(r => r.error);
		if (hasError) {
			return { status: 500, error: "Failed to create some equivalences" };
		}

		return { success: true };
	}
}