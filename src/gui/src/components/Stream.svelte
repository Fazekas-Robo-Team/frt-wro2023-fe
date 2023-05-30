<script lang="ts">
    import { onMount } from 'svelte';
    import { ws_url } from '../globals.js';
    import { subscribe } from 'svelte/internal';

    export let name: string;
    export let path: string;

    let timeout: any;
    let interval: any;
    let buffer: string[] = [];
    let buffer_size: number = NaN;
    let blob_url: string = "";

    function startBuffering () {
        timeout = setTimeout(() => {
            interval = setInterval(updateUrl, 0);
        }, 0);
    }

    function updateUrl () {
        if (buffer.length > 0) {
            blob_url = buffer.shift() as string;
            buffer_size = buffer.length;
        }
        if (buffer.length == 0) {
            clearInterval(interval);
            startBuffering();
        }
    }

    let subscribed = false;

    function connectStream () {

        if (!subscribed) {
            subscribed = true;
            ws_url.subscribe(connectStream);
        }

        let socket: WebSocket = new WebSocket($ws_url + '/stream' + path);

        socket.onmessage = event => {
            // Convert the received text to a base64-encoded binary string
            const binary = atob(event.data);

            // Convert the binary string to a Blob object
            const blob = new Blob([new Uint8Array(binary.length).map((_, i) => binary.charCodeAt(i))], { type: 'image/jpeg' });

            // Create a URL for the Blob object and set it as the source of an <img> element
            let url = URL.createObjectURL(blob);
            buffer.push(url);
        };

        startBuffering();
    }

    onMount(connectStream);
    
</script>

<figure>
    <img src="{blob_url}" alt="">
    <figcaption>{name} - buffer: {buffer_size}, url: {blob_url}</figcaption>
</figure>

<style>
    figure {
        width: 100%;
        padding: 0;
        margin: 0;
        text-align: center;
    }

    img {
        width: 100%;
        height: auto;
        border-radius: 12px;
    }

    figcaption {
        text-align: center;
        margin: 3px;
        padding: 0;
    }
</style>