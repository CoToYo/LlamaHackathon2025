import { NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';
import { splitIntoChunks } from '@/app/lib/textUtils';

export async function GET() {
  try {
    const scriptPath = path.join(process.cwd(), 'pitch_script.txt');
    const content = await fs.readFile(scriptPath, 'utf-8');
    const chunks = splitIntoChunks(content);
    return NextResponse.json({ chunks });
  } catch (error) {
    console.error('Error reading script:', error);
    return NextResponse.json({ error: 'Failed to read script' }, { status: 500 });
  }
} 