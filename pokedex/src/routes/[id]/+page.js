// @ts-nocheck
export async function load({ fetch, params }) {
	const id = params.id;
	const url = `https://pokeapi.co/api/v2/pokemon/${id}`;
	const url2 = `https://pokeapi.co/api/v2/pokemon-species/${id}`;
	const res = await fetch(url);
	const res2 = await fetch(url2);
	const pokeman = await res.json();
	const pokeman_flavor = await res2.json();

	console.log(pokeman);
	console.log(pokeman_flavor);
	return { pokeman, pokeman_flavor };
}