export function bigrams(text) {
  const chars = [...text.toLowerCase().replace(/\s+/g, '')]
  const set = new Set()
  for (let i = 0; i < chars.length - 1; i++) set.add(chars[i] + chars[i + 1])
  return set
}

export function bigramScore(query, text) {
  if (!query || !text) return 0
  const qGrams = bigrams(query)
  if (!qGrams.size) return 0
  const tGrams = bigrams(text)
  let hits = 0
  for (const g of qGrams) if (tGrams.has(g)) hits++
  return hits / qGrams.size
}
