import { defineConfig } from 'vite'

// Load plugin dynamically to avoid ESM/CJS interop issues on some environments
export default defineConfig(async () => {
  const reactPlugin = (await import('@vitejs/plugin-react')).default

  return {
    plugins: [reactPlugin()],

    server: {
      port: Number(process.env.FRONTEND_PORT) || 5173,

      // Allow Render's *.onrender.com hostname
      allowedHosts: ['.onrender.com'],

      proxy: {
        '/api': {
          target: process.env.VITE_API_TARGET || 'http://localhost:8000',
          changeOrigin: true,
        },
      },
    },
  }
})
