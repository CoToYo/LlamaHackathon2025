interface ScriptResponse {
	results: { result: string, raw: string }[];
	count: number;
}

export async function fetchScripts(): Promise<string | null> {
	try {
		const response = await fetch('https://s9tv8rcbh1.execute-api.us-east-1.amazonaws.com/prod/scripts');
		const data: ScriptResponse = await response.json();

		return data.results[0].result;
	} catch (error) {
		console.error('Error fetching scripts:', error);
		return null;
	}
}

export function formatScriptForSpeech(script: string): string {
	return script;
} 