import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  // tfjs is only reached via a lazy dynamic import in engine/classifier.ts, which Vite's dep
  // scanner doesn't always pre-bundle — list it so the dev server can serve the optimized dep
  // on demand (prod build already code-splits it correctly).
  optimizeDeps: {
    include: ['@tensorflow/tfjs'],
  },
})
