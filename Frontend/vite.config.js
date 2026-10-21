import react from '@vitejs/plugin-react'
import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [react()],
    server: {
      // Keep the browser on Vite's origin and forward API calls to Flask.
      // Set AETHER_BACKEND_URL when Flask runs somewhere other than localhost:5000.
      proxy: {
        '/api': {
          target: env.AETHER_BACKEND_URL || 'http://127.0.0.1:5000',
          changeOrigin: true,
        },
      },
    },
  }
})
