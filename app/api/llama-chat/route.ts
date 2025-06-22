import { NextRequest, NextResponse } from 'next/server';
import { LlamaClient, LlamaMessage } from '@/app/lib/llamaClient';

export async function POST(request: NextRequest) {
	try {
		const { messages } = await request.json();

		const client = new LlamaClient(
			process.env.LLAMA_API_URL || 'http://localhost:11434',
			process.env.LLAMA_API_KEY || ''
		);

		const response = await client.chat(messages);

		return NextResponse.json(response);
	} catch (error) {
		return NextResponse.json(
			{ error: 'Failed to get response from Llama' },
			{ status: 500 }
		);
	}
} 