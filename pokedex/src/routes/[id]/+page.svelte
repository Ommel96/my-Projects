<script>
	export let data;

	let types = [];
	let statName = [];
	let stats = [];

	for (let i = 0; i < data.pokeman.types.length; i++) {
		types.push(data.pokeman.types[i].type.url);
	}

	for (let i = 0; i < data.pokeman.stats.length; i++) {
		stats.push(data.pokeman.stats[i].base_stat);
		statName.push(data.pokeman.stats[i].stat.name);
	}

	if (data && data.pokeman && data.pokeman.types) {
		// @ts-ignore
		data.pokeman.types.forEach((typeInfo) => {
			const typeUrl = typeInfo?.type?.url?.split('/');
			if (typeUrl) {
				let typeNum = typeUrl[typeUrl.length - 2];
				types.push(
					`https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/types/generation-viii/brilliant-diamond-and-shining-pearl/${typeNum}.png`
				);
			}
		});
	}
</script>

<h1 class="text-4xl text-center my-8 uppercase">{data.pokeman?.name}</h1>

<div id="Card-Container" class="py-4 grid gap-4 md:grid-cols-2 grid-cols-1">
  
  <!-- Card for picture, flavor text and sound -->
  <div
    class="p-6 bg-gray-100 text-gray-800 text-center rounded-md shadow-sm hover:shadow-sm flex flex-col items-center"
  >
    <img src={data.pokeman.sprites['front_default']} alt={data.pokeman.name} class=" h-40 w-40" />
    
    <h2 class="text-2xl">
      {data.pokeman_flavor.flavor_text_entries[0].flavor_text.replace('\f', '\n')}
    </h2>
  </div>

  <!-- card for type and stats -->
	<div 
  class="text-center grid grid-rows-9 grid-cols-2 p-6 bg-gray-100 text-gray-800 rounded-md shadow-sm hover:shadow-sm"
  style="grid-template-columns: px 1fr;"
	>
			<p class="pr-2 text-left font-bold">Type:</p>

      <div class="flex items-center justify-start">
			{#each types as type}
				<img class="h-6 w-auto" src={type} alt="" />
			{/each}
      </div>

		<p class="text-right justify-self-start">
			<strong>Height</strong>: 
		</p>
    <p class="text-left">{data.pokeman.height}"</p>
    <p class="text-left">
      <strong>Weight</strong>: 
    </p>
    <p class="text-left">{data.pokeman.weight} pounds</p>
    
		{#each statName as stat, i}
			<p class="text-left"> 
        <strong>{stat}</strong>: 
      </p>
      <p class="text-left">
        {stats[i]}
      </p>
		{/each}
	</div>

</div>
<h1 class="text-center">Evolution Tree</h1>
<div 
class="py-4 grid gap-4 md:grid-cols-3 grid-cols-1">

	<div class="text-center p-6 bg-gray-100 text-gray-800 rounded-md shadow-sm hover:shadow-sm">
		<h1>Evolves from</h1>
		<h1 class="font-bold">{data.pokeman_flavor.evolves_from_species.name}</h1>
	</div>

	<div class="text-center p-6 bg-gray-100 text-gray-800 rounded-md shadow-sm hover:shadow-sm">current</div>

	<div class="text-center p-6 bg-gray-100 text-gray-800 rounded-md shadow-sm hover:shadow-sm">Evolves to</div>
</div>