import { client } from '$lib/api/client'
import type { components } from '$lib/api/schema';
import type { RequestEvent } from '@sveltejs/kit';

export const actions = {
	createScale: async ({ request }: RequestEvent) => {
		const data = await request.formData();
		const country_name = data.get('country_name') as string;
		const scale_description = data.get('scale_description') as string;
		const total_grades = data.get('total_grades') ? Number(data.get('total_grades')) : null; // NOTE: In the future utomatically generate this value


		const origin_grades = data.getAll('origin_grade') as string[];
		const spanish_5_10s = data.getAll('spanish_5_10') as string[];
		const spanish_1_4s = data.getAll('spanish_grade_1_4') as string[];
		const spanish_literals = data.getAll('spanish_literal') as string[];

		const equivalences = origin_grades.map((origin_grade, index) => {
			const origin_raw = origin_grade ?? '';
			const spanish5_raw = spanish_5_10s[index] ?? '';
			const spanish14_raw = spanish_1_4s[index] ?? '';
			const spanish_literal_raw = spanish_literals[index] ?? '';

			const origin = origin_raw.toString().trim();
			const spanish5 = spanish5_raw.toString().trim();
			const spanish14 = spanish14_raw.toString().trim();
			const spanishLiteral = spanish_literal_raw.toString().trim();

			return {
				origin_grade: origin,
				spanish_5_10: Number(spanish5),
				spanish_1_4: spanish14 ? parseInt(spanish14, 10) : null,
				spanish_literal: spanishLiteral as components['schemas']['SpanishLiteralEnum'],
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