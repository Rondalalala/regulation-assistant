import { createServer } from 'http'
import { readFileSync, existsSync } from 'fs'
import { join, extname } from 'path'

const DIST = join(import.meta.dirname, 'dist')
const PORT = 8080

const MIME = {
  '.html': 'text/html',
  '.js': 'application/javascript',
  '.css': 'text/css',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.json': 'application/json',
}

function readBody(req) {
  return new Promise((resolve) => {
    const chunks = []
    req.on('data', c => chunks.push(c))
    req.on('end', () => resolve(Buffer.concat(chunks)))
  })
}

function cleanReqHeaders(headers) {
  const h = { ...headers }
  delete h.host
  delete h['if-none-match']
  delete h['if-modified-since']
  delete h.connection
  delete h.origin
  delete h.referer
  return h
}

function cleanResHeaders(headers) {
  delete headers['content-encoding']
  delete headers['content-length']
  delete headers['transfer-encoding']
  headers['Access-Control-Allow-Origin'] = '*'
  return headers
}

createServer(async (req, res) => {
  // CORS preflight
  if (req.method === 'OPTIONS') {
    res.writeHead(200, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type,Authorization,User-Agent,X-Api-Base',
    })
    res.end()
    return
  }

  // Generic API proxy: reads target base URL from X-Api-Base header
  if (req.url.startsWith('/api-proxy/')) {
    const apiBase = req.headers['x-api-base']
    if (!apiBase) {
      res.writeHead(400, { 'Content-Type': 'application/json' })
      res.end(JSON.stringify({ error: 'Missing X-Api-Base header' }))
      return
    }
    const subPath = req.url.replace('/api-proxy/', '')
    const base = apiBase.replace(/\/+$/, '')
    const target = `${base}/${subPath}`

    try {
      const headers = cleanReqHeaders(req.headers)
      delete headers['x-api-base']

      const body = req.method !== 'GET' && req.method !== 'HEAD' ? await readBody(req) : undefined
      const apiRes = await fetch(target, { method: req.method, headers, body })
      const resBody = await apiRes.text()
      const resHeaders = {}
      apiRes.headers.forEach((v, k) => { resHeaders[k] = v })
      cleanResHeaders(resHeaders)
      res.writeHead(apiRes.status, resHeaders)
      res.end(resBody)
    } catch (e) {
      res.writeHead(502, { 'Content-Type': 'application/json' })
      res.end(JSON.stringify({ error: e.message }))
    }
    return
  }

  // Static files
  let filePath = join(DIST, req.url === '/' ? 'index.html' : req.url)
  if (!existsSync(filePath)) filePath = join(DIST, 'index.html')
  const ext = extname(filePath)
  try {
    const data = readFileSync(filePath)
    res.writeHead(200, { 'Content-Type': MIME[ext] || 'application/octet-stream' })
    res.end(data)
  } catch {
    res.writeHead(404)
    res.end('Not found')
  }
}).listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`)
  console.log(`API proxy: /api-proxy/* → reads target from X-Api-Base header`)
})
