import { json } from '@sveltejs/kit';
import { client } from '$lib/api/client';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ url }) => {
	const skip = Number(url.searchParams.get('skip') ?? 0);
	const limit = Number(url.searchParams.get('limit') ?? 20);

	const { data, error } = await client.GET('/scales/', {
		params: { query: { skip, limit } }
	});

	if (error || !data) {
		return json([], { status: 500 });
	}

	return json(data);
};
