import { writable } from 'svelte/store';

export const api_url = writable('http://192.168.1.209:8000');
export const ws_url = writable('ws://192.168.1.209:8000');
