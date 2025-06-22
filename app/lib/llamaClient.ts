export interface LlamaMessage {
	role: 'user' | 'assistant' | 'system';
	content: string;
}

export interface LlamaResponse {
	content: string;
	usage?: {
		prompt_tokens: number;
		completion_tokens: number;
		total_tokens: number;
	};
}

export class LlamaClient {
	private baseUrl: string;
	private apiKey: string;

	constructor(baseUrl: string, apiKey: string) {
		this.baseUrl = baseUrl;
		this.apiKey = apiKey;
	}

	async chat(messages: LlamaMessage[]): Promise<LlamaResponse> {
		const response = await fetch(`${this.baseUrl}/v1/chat/completions`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Authorization': `Bearer ${this.apiKey}`,
			},
			body: JSON.stringify({
				model: 'llama-3.1-8b-instruct',
				messages,
				max_tokens: 1000,
				temperature: 0.7,
			}),
		});

		if (!response.ok) {
			throw new Error(`Llama API error: ${response.status}`);
		}

		const data = await response.json();
		return {
			content: data.choices[0].message.content,
			usage: data.usage,
		};
	}
} 