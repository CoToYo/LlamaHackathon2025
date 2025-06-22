interface Comment {
  comment_id: string;
  question: string;
  answer: string;
  ttl: number;
  status: string;
  timestamp: number;
}

interface CommentsResponse {
  responses: Comment[];
}

export async function fetchComments(): Promise<Comment[]> {
  try {
    const response = await fetch('https://s9tv8rcbh1.execute-api.us-east-1.amazonaws.com/prod/responses');
    const data: CommentsResponse = await response.json();

    // Return full comment objects including comment_id
    return data.responses;
  } catch (error) {
    console.error('Error fetching comments:', error);
    return [];
  }
}

export function formatCommentForSpeech(comment: Comment): string {
  return `We hear some users asked ${comment.question}, ${comment.answer}`;
} 