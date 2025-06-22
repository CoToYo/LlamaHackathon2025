import { llamaChat, Message } from "@/app/lib/llamaApi";

export async function POST(request: Request): Promise<Response> {
	try {
		const body: { messages: Message[] } = await request.json();
		const { messages } = body;

		if (!messages || messages.length === 0) {
			return new Response(JSON.stringify({ error: 'Messages are required' }), {
				status: 400,
				headers: { 'Content-Type': 'application/json' },
			});
		}

		const completion = await llamaChat(messages);

		return new Response(JSON.stringify({ content: completion.content }), {
			status: 200,
			headers: { 'Content-Type': 'application/json' },
		});
	} catch (error) {
		console.error('Error in Llama chat API:', error);
		const errorMessage = error instanceof Error ? error.message : 'Internal server error';
		return new Response(JSON.stringify({ error: errorMessage }), {
			status: 500,
			headers: { 'Content-Type': 'application/json' },
		});
	}
} 