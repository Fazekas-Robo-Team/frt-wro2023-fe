<script lang="ts">
    import { api_url } from '../globals.js';
    import { ws_url } from '../globals.js';

    function handleSumbit (event: Event) {
        event.preventDefault();
        const form = event.target as HTMLFormElement;
        const data = new FormData(form);
        const url = form.action;
        const method = form.method;
        fetch(url, {
            method: method,
            body: data
        })
    }
</script>

<div class="wrapper">
    <span>Backend URL</span>
    <input type="text" bind:value={$api_url}>
    <span>Websocket URL</span>
    <input type="text" bind:value={$ws_url}>

    <span>Settings</span>
    <form action="{$api_url}/settings" method="post" on:submit|preventDefault={handleSumbit}>
        <label>Width<input type="number" name="width"></label>
        <label>Height<input type="number" name="height" ></label>
        <label>FOV<input type="text" name="fov"></label>
        <label>Cut height<input type="number" name="cut_frame_height"></label>
        <label>OpenCV Threads<input type="number" name="opencv_threads"></label>
        <label>Picamera2 Threads<input type="number" name="picamera2_threads"></label>
        <label>Framerate<input type="number" name="framerate"></label>
        <input class="button" type="submit" value="Save">
    </form>
</div>

<style>
    .wrapper {
        width: 100%;
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background-color: #444654;
        border-radius: 12px;
    }

    input {
        margin: 6px;
    }

    form {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    .button {
        margin: 6px;
        padding: 6px;
        border-radius: 6px;
        background-color: #444654;
        color: white;
        border: 1px solid white;
    }
</style>