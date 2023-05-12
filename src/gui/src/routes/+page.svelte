<script>
    import Settings from "../components/Settings.svelte";
    import Streams from "../components/Streams.svelte";
    import Stats from "../components/Stats.svelte";
    import Scene from "../components/Scene.svelte";
</script>

<div class="left-column">
    <Scene />
    <Streams />
</div>

<div class="right-column">
    <Settings />
    <Stats />
</div>

<style>
    .left-column {
        width: 55%;
        padding: 6px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .right-column {
        display: flex;
        flex-direction: column;
        justify-content: center;
        flex: 1;
        padding: 6px;
    }
</style>
