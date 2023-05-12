<Header />

<main>
  <slot />
</main>

<Footer />

<style>

</style>

<script>
  export const title = 'My SvelteKit App';
  import Header from './components/Header.svelte';
  import Footer from './components/Footer.svelte';
</script>