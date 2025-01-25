import { createApp } from 'vue'
import App from './App.vue'
import axios from "axios";

const app = createApp(App)

axios.defaults.withCredentials = true;
axios.defaults.baseURL = 'http://localhost:8000';  // the FastAPI backend

app.mount('#app')
