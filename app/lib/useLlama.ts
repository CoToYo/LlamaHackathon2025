import { useState } from 'react';
import { LlamaMessage } from './llamaClient';

interface ChatOptions {
	model?: string;
	max_tokens?: number;
}

export function useLlama() {
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);

	const sendMessage = async (
		messages: LlamaMessage[],
		options?: ChatOptions
	) => {
		setLoading(true);
		setError(null);

		try {
			const response = await fetch('/chat/completions', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					messages,
					model: options?.model ?? 'Llama-3.3-8B-Instruct',
					max_tokens: options?.max_tokens ?? 256,
				}),
			});

			if (!response.ok) throw new Error('Failed to get response');

			const data = await response.json();
			return data;
		} catch (err) {
			setError(err instanceof Error ? err.message : 'Unknown error');
			return null;
		} finally {
			setLoading(false);
		}
	};

	return { sendMessage, loading, error };
}
