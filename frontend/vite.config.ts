import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath } from 'url'
import { dirname, resolve } from 'path'
import history from 'connect-history-api-fallback'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    {
      name: 'configure-history-fallback',
      configureServer(server) {
        return () => {
          server.middlewares.use(
            history({
              rewrites: [
                { 
                  from: /^\/(assets|images|css|js)\/.*/, 
                  to: (context) => context.parsedUrl.pathname 
                },
                { from: /./, to: '/index.html' }
              ]
            })
          )
        }
      }
    }
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
    },
  },
  server: {
    port: 8201,
    cors: true,
    hmr: false,
    proxy: {
      '/api': {
        target: 'http://localhost:8200',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8200',
        ws: true,
      }
    }
  }
})
