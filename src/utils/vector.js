/**
 * Decode base64 binary vector to Uint8Array.
 * Each bit represents the sign of one dimension (1 = positive, 0 = negative).
 */
function decodeBvec(bvec) {
  const bin = atob(bvec)
  const arr = new Uint8Array(bin.length)
  for (let i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i)
  return arr
}

/**
 * Hamming similarity between two binary vectors.
 * Returns the fraction of matching bits (0..1, higher = more similar).
 */
function hammingSim(a, b) {
  let match = 0
  const total = a.length * 8
  for (let i = 0; i < a.length; i++) {
    match += 8 - popcount(a[i] ^ b[i])
  }
  return match / total
}

function popcount(n) {
  n = n - ((n >> 1) & 0x55)
  n = (n & 0x33) + ((n >> 2) & 0x33)
  return ((n + (n >> 4)) & 0x0F)
}

/**
 * Return top-k items most similar to query's binary vector.
 * @param {string} queryBvec - base64 encoded binary vector
 * @param {{bvec: string}[]} items
 * @param {number} [k=8]
 */
export function topK(queryBvec, items, k = 8) {
  const qBytes = decodeBvec(queryBvec)
  const scored = items.map((item, index) => ({
    index,
    score: hammingSim(qBytes, decodeBvec(item.bvec)),
    item,
  }))
  scored.sort((a, b) => b.score - a.score)
  return scored.slice(0, k)
}
