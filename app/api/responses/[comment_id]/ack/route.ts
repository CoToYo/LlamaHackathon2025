import { NextRequest, NextResponse } from 'next/server';

export async function POST(
	request: NextRequest,
	{ params }: { params: { comment_id: string } }
) {
	try {
		const { comment_id } = params;

		if (!comment_id) {
			return NextResponse.json(
				{ error: 'Comment ID is required' },
				{ status: 400 }
			);
		}

		// Make the acknowledgment request to the external API
		const response = await fetch(
			`https://s9tv8rcbh1.execute-api.us-east-1.amazonaws.com/prod/responses/${comment_id}/ack`,
			{
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
			}
		);

		if (!response.ok) {
			console.error(`Failed to acknowledge comment ${comment_id}:`, response.status, response.statusText);
			return NextResponse.json(
				{ error: `Failed to acknowledge comment: ${response.statusText}` },
				{ status: response.status }
			);
		}

		console.log(`Successfully acknowledged comment: ${comment_id}`);
		return NextResponse.json({ success: true, comment_id });

	} catch (error) {
		console.error('Error acknowledging comment:', error);
		return NextResponse.json(
			{ error: 'Internal server error' },
			{ status: 500 }
		);
	}
} 