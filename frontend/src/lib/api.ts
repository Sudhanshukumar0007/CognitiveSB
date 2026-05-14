export const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

export interface Node {
  id: string;
  label: string;
  group?: string;
  [key: string]: unknown;
}

export interface Link {
  source: string;
  target: string;
  label?: string;
}

export interface Flashcard {
  id: string;
  front: string;
  back: string;
  explanation?: string;
  hint?: string;
  mastery: number;
  next_review: string;
}

export interface MCQ {
  id: string;
  question: string;
  options: string[];
  answer: number;
  difficulty?: 'easy' | 'medium' | 'hard' | string;
  explanation?: string;
}

export interface ShortAnswer {
  id: string;
  question: string;
  sample_answer: string;
}

export interface GradeResult {
  score: number;
  feedback: string;
  correct_concepts: string[];
  missed_concepts: string[];
  study_tip?: string;
}

export interface Session {
  id: string;
  title: string;
  original_filename?: string;
  created_at: string;
  chunk_count: number;
}

export interface NotePoint {
  bullet: string;
  explanation: string;
  example?: string;
  importance?: string;
}

export interface NotesResponse {
  points?: NotePoint[];
  key_points?: string[];
  summary?: string;
  real_world_examples?: string[];
}

export interface Citation {
  text: string;
  page?: number | string | null;
  source?: string;
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let message = response.statusText;
    try {
      const errorData = await response.json();
      message = errorData.message || errorData.error || message;
    } catch {
      // Ignore json parse error
    }
    throw { error: 'api_error', message };
  }
  return response.json();
}

export async function uploadFile(file: File): Promise<{session_id: string, title: string, chunk_count: number}> {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${BASE_URL}/upload`, {
    method: 'POST',
    body: formData,
  });
  return handleResponse(response);
}

export async function uploadYouTube(url: string): Promise<{session_id: string, title: string, chunk_count: number}> {
  const response = await fetch(`${BASE_URL}/upload`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ youtube_url: url }),
  });
  return handleResponse(response);
}

export function streamChat(
  message: string,
  sessionId: string,
  mode: 'socratic' | 'feynman' | 'simple' | 'exam',
  onToken: (token: string) => void,
  onDone: () => void,
  onError: (err: string) => void,
  onCitations?: (citations: Citation[]) => void
): void {
  const url = new URL(`${BASE_URL}/chat`);
  url.searchParams.append('message', message);
  url.searchParams.append('session_id', sessionId);
  url.searchParams.append('mode', mode);

  const eventSource = new EventSource(url.toString());

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      if (data.error) {
        onError(data.error);
        eventSource.close();
        return;
      }
      if (data.done) {
        onDone();
        eventSource.close();
      } else if (data.token) {
        onToken(data.token);
      }
    } catch {
      onError('Failed to parse SSE data');
      eventSource.close();
    }
  };

  eventSource.onerror = () => {
    onError('Connection lost');
    eventSource.close();
  };

  eventSource.addEventListener('citations', (event) => {
    try {
      onCitations?.(JSON.parse(event.data));
    } catch {
      onCitations?.([]);
    }
  });
}

export async function getGraph(sessionId: string): Promise<{nodes: Node[], links: Link[]}> {
  const response = await fetch(`${BASE_URL}/graph/${sessionId}`);
  return handleResponse(response);
}

export async function generateGraph(sessionId: string): Promise<{nodes: Node[], links: Link[]}> {
  const response = await fetch(`${BASE_URL}/graph/generate/${sessionId}`, { method: 'POST' });
  return handleResponse(response);
}

export async function getFlashcards(sessionId: string): Promise<{cards: Flashcard[]}> {
  const response = await fetch(`${BASE_URL}/flashcards/${sessionId}`);
  return handleResponse(response);
}

export async function generateFlashcards(sessionId: string): Promise<{cards: Flashcard[]}> {
  const response = await fetch(`${BASE_URL}/flashcards/generate/${sessionId}`, { method: 'POST' });
  return handleResponse(response);
}

export async function rateFlashcard(cardId: string, sessionId: string, mastery: number): Promise<{next_review: string}> {
  const response = await fetch(`${BASE_URL}/flashcards/rate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ card_id: cardId, session_id: sessionId, mastery }),
  });
  return handleResponse(response);
}

export async function getQuiz(sessionId: string): Promise<{mcq: MCQ[], short_answer: ShortAnswer[]}> {
  const response = await fetch(`${BASE_URL}/quiz/${sessionId}`);
  return handleResponse(response);
}

export async function generateQuiz(sessionId: string, options: { difficulty: string, count: number }): Promise<{mcq: MCQ[], short_answer: ShortAnswer[]}> {
  const response = await fetch(`${BASE_URL}/quiz/generate/${sessionId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(options),
  });
  return handleResponse(response);
}

export async function gradeAnswer(question: string, userAnswer: string, sampleAnswer: string, sessionId?: string): Promise<GradeResult> {
  const response = await fetch(`${BASE_URL}/quiz/grade`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, user_answer: userAnswer, sample_answer: sampleAnswer, session_id: sessionId }),
  });
  return handleResponse(response);
}

export async function getNotes(sessionId: string): Promise<NotesResponse> {
  const response = await fetch(`${BASE_URL}/notes/${sessionId}`);
  return handleResponse(response);
}

export async function generateNotes(sessionId: string): Promise<NotesResponse> {
  const response = await fetch(`${BASE_URL}/notes/generate/${sessionId}`, { method: 'POST' });
  return handleResponse(response);
}

export async function getSessions(): Promise<{sessions: Session[]}> {
  const response = await fetch(`${BASE_URL}/sessions`);
  return handleResponse(response);
}

export async function deleteSession(sessionId: string): Promise<{deleted: boolean}> {
  const response = await fetch(`${BASE_URL}/sessions/${sessionId}`, {
    method: 'DELETE',
  });
  return handleResponse(response);
}

export async function getFact(sessionId: string): Promise<{ fact: string }> {
  const res = await fetch(`${BASE_URL}/fact/${sessionId}`)
  if (!res.ok) throw new Error('Failed to fetch fact')
  return res.json()
}

export async function getProgress(sessionId: string): Promise<{ quiz_avg: number, mastery_pct: number }> {
  const response = await fetch(`${BASE_URL}/progress/${sessionId}`);
  return handleResponse(response);
}
