import { createApp } from 'vue';
import { clerkPlugin } from '@clerk/vue';
import { esES } from '@clerk/localizations';
import './style.css';
import App from './App.vue';

// Clave publicable: está pensada para viajar en el bundle. La secreta nunca va aquí.
const publishableKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;
if (!publishableKey) {
  throw new Error('Falta VITE_CLERK_PUBLISHABLE_KEY en el archivo .env');
}

createApp(App).use(clerkPlugin, { publishableKey, localization: esES }).mount('#app');
