<script>
// @ts-nocheck

    import PokemanCard from "./components/PokemanCard.svelte";
    import { pokemon } from "../stores/pokestores";

    let searchTerm = "";
    let filteredPokemon = [];

    $: {
        console.log(searchTerm);
        if(searchTerm) {
            filteredPokemon = $pokemon.filter(pokeman => pokeman.
            name.toLowerCase().includes(searchTerm.toLowerCase()));
        }else {
            filteredPokemon = [...$pokemon]
        }
    }
 
</script>

<svelte:head>
    <title>Pokedex</title>
</svelte:head>

<h1 class=" text-4xl text-center my-8 uppercase">Pokédex</h1>

<input class="w-full rounded-md text-lg p-4 border-2 border-gray-200" type="text" bind:value={searchTerm} placeholder="Search Pokemon">

<div class="py-4 grid gap-4 md:grid-cols-2 grid-cols-1">
    {#each filteredPokemon as pokeman}
    <p>
        <PokemanCard pokeman={pokeman} />
    </p>
    {/each}
</div>