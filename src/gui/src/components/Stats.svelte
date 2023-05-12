<script>
    import { onMount } from "svelte";
    import { api_url } from "../globals";

    let fps = NaN;
    let skipped_frames = NaN;
    let skipped_frames_percent = NaN;
    
    onMount(async () => {
        const interval = setInterval(async () => {
            let response = await fetch(`${$api_url}/stats`);
            let data = await response.json();
            fps = data.avg_fps;
            skipped_frames = data.skipped_frames;
            skipped_frames_percent = data.skipped_frames_percent;
        }, 1000);
    });

    function resetStats() {
        fetch(`${$api_url}/reset_stats`, {
            method: "POST"
        });
    }

</script>

<div class="wrapper">
    <p>Average FPS: {fps}</p>
    <p>Skipped Frames: {skipped_frames} ({skipped_frames_percent}%)</p>
    <button on:click={resetStats}>Reset Stats</button>
</div>

<style>
    .wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background-color: #444654;
        margin-top: 12px;
        padding: 12px;
        flex: 1;
        border-radius: 12px;
    }

    button {
        margin-top: 12px;
        padding: 6px;
        border-radius: 6px;
        background-color: #444654;
        color: white;
        border: 1px solid white;
        font-size: 1em;
    }
</style>