import { client } from '$lib/api/client'
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