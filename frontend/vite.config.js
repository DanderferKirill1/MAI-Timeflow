import { defineConfig } from 'vite'
import path from 'path'

export default defineConfig({
  root: path.resolve(__dirname, 'templates'),
  publicDir: path.resolve(__dirname, '../public'),
  server: {
    port: 5500,
    fs: {
      allow: ['..'],
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
    }
  },
  build: {
    outDir: '../../dist',
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, 'templates/index.html')
      }
    }
  }
})