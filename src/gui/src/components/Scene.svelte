<script lang="ts">
    import { onMount } from 'svelte';

    // @ts-ignore
    import * as THREE from 'three';

    let canvas_div: HTMLDivElement;
    let x = NaN, y = NaN, z = NaN;

    onMount(() => {
        const scene = new THREE.Scene();

        const renderer = new THREE.WebGLRenderer({
            antialias: true
        });
        renderer.setClearColor(0x000000);

        const camera = new THREE.PerspectiveCamera(75, canvas_div.clientWidth / canvas_div.clientHeight, 0.1, 1000);
        canvas_div.appendChild(renderer.domElement);
        
        // Create a box to show the camera's position
        const boxGeometry = new THREE.BoxGeometry(3, 3, 3);
        const boxMaterial = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
        const box = new THREE.Mesh(boxGeometry, boxMaterial);
        scene.add(box);

        // Set the initial camera position and rotation
        camera.position.set(0, 0, 10);
        camera.lookAt(box.position);

        // Define the movement speed
        const moveSpeed = 0.1;
        const rotateSpeed = 0.01;

        // Listen for keyboard events
        const keyboard: any = {};
        document.addEventListener('keydown', event => {
            keyboard[event.key] = true;
        });
        document.addEventListener('keyup', event => {
            keyboard[event.key] = false;
        });

        // Listen for mouse events
        let mouseDown = false;
        let lastMouseX: number, lastMouseY: number;
        document.addEventListener('mousedown', event => {
            mouseDown = true;
            lastMouseX = event.clientX;
            lastMouseY = event.clientY;
        });
        document.addEventListener('mouseup', event => {
            mouseDown = false;
        });
        document.addEventListener('mousemove', event => {
            if (mouseDown) {
                
            }
        });

        // Define the main animation loop
        function animate() {
            requestAnimationFrame(animate);

            // Move the camera based on keyboard input
            if (keyboard['w']) {
                camera.position.add(camera.getWorldDirection(new THREE.Vector3()).multiplyScalar(moveSpeed));
            }
            if (keyboard['s']) {
                camera.position.add(camera.getWorldDirection(new THREE.Vector3()).multiplyScalar(-moveSpeed));
            }
            if (keyboard['a']) {
                const axis = new THREE.Vector3(1, 0, 0).applyQuaternion(camera.quaternion);
                camera.position.add(axis.multiplyScalar(-moveSpeed));
            }
            if (keyboard['d']) {
                const axis = new THREE.Vector3(1, 0, 0).applyQuaternion(camera.quaternion);
                camera.position.add(axis.multiplyScalar(moveSpeed));
            }

            // rounded
            x = Math.round(camera.position.x * 100) / 100;
            y = Math.round(camera.position.y * 100) / 100;
            z = Math.round(camera.position.z * 100) / 100;

            renderer.setSize(canvas_div.clientWidth, canvas_div.clientHeight);
            renderer.render(scene, camera);
        }

        animate();
    });

    
    
</script>

<div class="wrapper">
    <div class="canvas" bind:this={canvas_div}></div>
    <p>x: {x}, y: {y}, z: {z}</p>
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

    .canvas {
        width: 100%;
        height: 100%;
        border-radius: 12px;
    }
</style>