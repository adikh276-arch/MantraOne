import { useMutation, useQuery } from '@tanstack/react-query';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/v1';

async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.detail || 'API request failed');
  }

  return response.json();
}

// --- Chat APIs ---
export interface SendMessagePayload {
  family_id: string;
  member_id: string;
  message: string;
}

export interface ChatResponse {
  message_id: string;
  content: string;
  status: string;
}

export function useSendMessage() {
  return useMutation({
    mutationFn: (payload: SendMessagePayload) =>
      fetchApi<ChatResponse>('/chat', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
  });
}

// --- Upload APIs ---
export function useUploadDocument() {
  return useMutation({
    mutationFn: async ({ file, family_id, member_id }: { file: File; family_id: string; member_id: string }) => {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('family_id', family_id);
      formData.append('member_id', member_id);

      const response = await fetch(`${BASE_URL}/documents/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      return response.json();
    },
  });
}
