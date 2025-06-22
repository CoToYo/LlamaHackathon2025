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

export async function fetchComments(): Promise<{ question: string; answer: string }[]> {
  try {
    const response = await fetch('https://s9tv8rcbh1.execute-api.us-east-1.amazonaws.com/prod/responses');
    const data: CommentsResponse = await response.json();

    // Extract only question and answer fields
    return data.responses.map(comment => ({
      question: comment.question,
      answer: comment.answer
    }));
  } catch (error) {
    console.error('Error fetching comments:', error);
    return [];
  }
}

export function formatCommentForSpeech(comment: { question: string; answer: string }): string {
  return `We hear some users asked ${comment.question}, ${comment.answer}`;
} 