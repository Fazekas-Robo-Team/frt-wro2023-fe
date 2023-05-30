import { writable } from 'svelte/store';

export const api_url = writable('http://pi.local:8000');
export const ws_url = writable('ws://pi.local:8000');
