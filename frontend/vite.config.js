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