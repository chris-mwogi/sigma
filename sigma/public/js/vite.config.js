import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    outDir: '../dist',
    target: 'es2017',
    emptyOutDir: false,
    rollupOptions: {
      input: path.resolve(__dirname, 'src/main.js'),
      output: {
        format: 'iife',
        entryFileNames: 'sigma-app.js',
        chunkFileNames: 'sigma-app-[name].js',
        assetFileNames: (assetInfo) => {
          if (assetInfo.name && assetInfo.name.endsWith('.css')) {
            return 'sigma-app.css'
          }
          return '[name].[ext]'
        },
        name: 'SigmaApp',
      },
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})

