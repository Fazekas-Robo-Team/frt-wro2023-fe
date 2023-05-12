<script>
    // three.js demo
    // @ts-ignore
    import * as THREE from 'three';

    const scene = new THREE.Scene();

    const renderer = new THREE.WebGLRenderer();
</script>

<div class="wrapper">
    <canvas id="canvas"></canvas>
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

    canvas {
        width: 100%;
        height: 100%;
    }
</style>