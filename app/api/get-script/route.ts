import { NextResponse } from 'next/server';
import { fetchScripts } from '@/app/lib/scriptApi';
import { splitIntoChunks } from '@/app/lib/textUtils';

export async function GET() {
  try {
    const scriptText = await fetchScripts();
    if (!scriptText) {
      return NextResponse.json({ error: 'Failed to fetch script from API' }, { status: 500 });
    }

    const chunks = splitIntoChunks(scriptText, 100); // 100 words per chunk
    return NextResponse.json({ chunks });
  } catch (error) {
    console.error('Error fetching script:', error);
    return NextResponse.json({ error: 'Failed to fetch script' }, { status: 500 });
  }
} 