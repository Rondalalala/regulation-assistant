import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { viteSingleFile } from 'vite-plugin-singlefile'

function corsProxyPlugin() {
  return {
    name: 'cors-proxy',
    configureServer(server) {
      server.middlewares.use('/api-proxy', async (req, res) => {
        if (req.method === 'OPTIONS') {
          res.writeHead(200, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization,User-Agent,X-Api-Base',
          })
          res.end()
          return
        }
        const apiBase = req.headers['x-api-base']
        if (!apiBase) {
          res.writeHead(400, { 'Content-Type': 'application/json' })
          res.end(JSON.stringify({ error: 'Missing X-Api-Base header' }))
          return
        }
        try {
          const base = apiBase.replace(/\/+$/, '')
          const subPath = req.url.slice(1) // remove leading /
          const target = `${base}/${subPath}`
          const headers = { ...req.headers }
          delete headers.host; delete headers.connection; delete headers.origin; delete headers.referer; delete headers['x-api-base']
          const chunks = []
          for await (const c of req) chunks.push(c)
          const body = chunks.length ? Buffer.concat(chunks) : undefined
          const apiRes = await fetch(target, { method: req.method, headers, body })
          const resBody = await apiRes.text()
          const resHeaders = {}
          apiRes.headers.forEach((v, k) => { resHeaders[k] = v })
          delete resHeaders['content-encoding']; delete resHeaders['content-length']; delete resHeaders['transfer-encoding']
          resHeaders['Access-Control-Allow-Origin'] = '*'
          res.writeHead(apiRes.status, resHeaders)
          res.end(resBody)
        } catch (e) {
          res.writeHead(502, { 'Content-Type': 'application/json' })
          res.end(JSON.stringify({ error: e.message }))
        }
      })
    },
  }
}

export default defineConfig({
  plugins: [vue(), viteSingleFile(), corsProxyPlugin()],
  base: './',
  build: {
    chunkSizeWarningLimit: 20000,
    assetsInlineLimit: 100000000,
    cssCodeSplit: false,
  },
})
