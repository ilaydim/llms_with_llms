import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const API_PATHS = ['/students', '/sessions', '/dialogue', '/quiz', '/survey', '/progress', '/tasks', '/health']

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: Object.fromEntries(
      API_PATHS.map((p) => [p, { target: 'http://127.0.0.1:8000', changeOrigin: true }])
    ),
  },
})
