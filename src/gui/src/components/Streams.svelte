<script>
  import Stream from "./Stream.svelte";
</script>

<div class="wrapper">
    <Stream name="1/8 Raw" path="/full"/>
    <Stream name="1/4 Red Mask" path="/red_mask"/>
    <Stream name="1/4 Green Mask" path="/green_mask"/>
    <Stream name="1/4 Boundary Boxes" path="/contours"/>
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
        border-radius: 12px;
        flex: 1;
    }
</style>


