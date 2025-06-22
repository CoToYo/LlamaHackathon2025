/**
 * Splits text into chunks of approximately the specified word count,
 * only breaking at sentence boundaries.
 */
export function splitIntoChunks(text: string, maxWordsPerChunk: number = 50): string[] {
  // Split into sentences (handling multiple punctuation marks)
  const sentences = text.match(/[^.!?]+[.!?]+/g) || [];
  const chunks: string[] = [];
  let currentChunk: string[] = [];
  let currentWordCount = 0;

  for (const sentence of sentences) {
    const trimmedSentence = sentence.trim();
    const sentenceWordCount = trimmedSentence.split(/\s+/).length;

    // If adding this sentence would exceed the limit, start a new chunk
    if (currentWordCount + sentenceWordCount > maxWordsPerChunk && currentChunk.length > 0) {
      chunks.push(currentChunk.join(' '));
      currentChunk = [];
      currentWordCount = 0;
    }

    currentChunk.push(trimmedSentence);
    currentWordCount += sentenceWordCount;
  }

  // Add the last chunk if there's anything left
  if (currentChunk.length > 0) {
    chunks.push(currentChunk.join(' '));
  }

  return chunks;
} 