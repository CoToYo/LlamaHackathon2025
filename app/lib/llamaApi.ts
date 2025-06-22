export interface Message {
	role: "user" | "assistant" | "system";
	content: string;
}

interface LlamaChatRequest {
	model: string;
	messages: Message[];
	stream?: boolean;
}

interface LlamaCompletionMessage {
	role: "assistant";
	content: string;
	stop_reason?: "stop" | "tool_calls" | "length";
}

interface LlamaChatResponse {
	choices: { message: LlamaCompletionMessage }[];
}

const LLAMA_API_URL = "https://api.llama.com/compat/v1/chat/completions";

export async function llamaChat(
	messages: Message[],
	model: string = "Llama-4-Maverick-17B-128E-Instruct-FP8",
): Promise<LlamaCompletionMessage> {
	if (!process.env.LLAMA_API_KEY) {
		throw new Error("LLAMA_API_KEY is not set in environment variables.");
	}

	const requestBody: LlamaChatRequest = {
		model,
		messages,
	};

	const response = await fetch(LLAMA_API_URL, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			Authorization: `Bearer ${process.env.LLAMA_API_KEY}`,
		},
		body: JSON.stringify(requestBody),
	});

	if (!response.ok) {
		const errorText = await response.text();
		throw new Error(`Llama API request failed: ${response.status} ${errorText}`);
	}

	const data: LlamaChatResponse = await response.json();
	return data.choices[0].message;
}
