import { client } from "$lib/api/client";
import type { components } from "$lib/api/schema";
import type { PageServerLoad, Actions } from "./$types";
import type { RequestEvent } from "@sveltejs/kit";

export const load: PageServerLoad = async ({ params }) => {
    const scaleId = Number(params.scale_id);
    if (!Number.isFinite(scaleId)) {
        return { status: 400, error: "Invalid scale id" };
    }

    const { data, error } = await client.GET("/scales/{scale_id}", {
        params: { path: { scale_id: scaleId } }
    });

    if (error || !data) {
        return { status: 500, error };
    }

    return { scale: data };
};

export const actions: Actions = {
    addEquivalences: async ({ params, request }: RequestEvent) => {
        const scaleId = Number(params.scale_id);
        if (!Number.isFinite(scaleId)) {
            return { status: 400, error: "Invalid scale id" };
        }

        const data = await request.formData();
        const origin_grades = data.getAll("origin_grade") as string[];
        const spanish_5_10s = data.getAll("spanish_grade_5_10") as string[];
        const spanish_1_4s = data.getAll("spanish_grade_1_4") as string[];
        const spanish_literals = data.getAll("spanish_literal") as string[];

        const equivalences = origin_grades.map((origin_grade, index) => {
            const origin_raw = origin_grade ?? "";
            const spanish5_raw = spanish_5_10s[index] ?? "";
            const spanish14_raw = spanish_1_4s[index] ?? "";
            const spanish_literal_raw = spanish_literals[index] ?? "";

            const origin = origin_raw.toString().trim();
            const spanish5 = spanish5_raw.toString().trim();
            const spanish14 = spanish14_raw.toString().trim();
            const spanishLiteral = spanish_literal_raw.toString().trim();

            return {
                origin_grade: origin,
                spanish_5_10: Number(spanish5),
                spanish_1_4: spanish14 ? parseInt(spanish14, 10) : null,
                spanish_literal: spanishLiteral as components["schemas"]["SpanishLiteralEnum"],
            };
        });

        if (equivalences.length === 0) {
            return { status: 400, error: "Add at least one equivalence." };
        }

        const results = await Promise.all(
            equivalences.map((eq) =>
                client.POST("/scales/{scale_id}/equivalences/", {
                    params: {
                        path: { scale_id: scaleId }
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

        const hasError = results.some((result) => result.error);
        if (hasError) {
            return { status: 500, error: "Failed to create some equivalences." };
        }

        return { success: equivalences.length };
    }
};
