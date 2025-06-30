/**
 * AI Assistant component for Smart CRM SaaS application.
 * Provides UI to interact with backend AI assistant API for:
 * - Message summaries
 * - Follow-up reminders
 * - Invoice text generation
 */

'use client';

import React, { useState } from 'react';
import { apiClient } from '@/lib/api-client';

interface AIResponse {
  output_text: string;
}

export const AIAssistant: React.FC = () => {
  const [inputText, setInputText] = useState('');
  const [actionType, setActionType] = useState<'message_summary' | 'follow_up_reminder' | 'invoice_text_generation'>('message_summary');
  const [relatedId, setRelatedId] = useState<number | null>(null);
  const [response, setResponse] = useState<AIResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const data = await apiClient.getAIAssistantResponse(actionType, inputText, relatedId ?? undefined);
      setResponse(data);
    } catch (err: any) {
      setError(err.message || 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 border rounded-md shadow-md bg-white max-w-lg mx-auto">
      <h2 className="text-xl font-semibold mb-4">AI Assistant</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="actionType" className="block font-medium mb-1">Action Type</label>
          <select
            id="actionType"
            value={actionType}
            onChange={(e) => setActionType(e.target.value as any)}
            className="w-full border rounded px-3 py-2"
          >
            <option value="message_summary">Message Summary</option>
            <option value="follow_up_reminder">Follow-up Reminder</option>
            <option value="invoice_text_generation">Invoice Text Generation</option>
          </select>
        </div>

        <div>
          <label htmlFor="inputText" className="block font-medium mb-1">Input Text</label>
          <textarea
            id="inputText"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            rows={4}
            className="w-full border rounded px-3 py-2"
            placeholder="Enter text for AI processing"
            required={actionType === 'message_summary'}
            disabled={actionType !== 'message_summary'}
          />
        </div>

        <div>
          <label htmlFor="relatedId" className="block font-medium mb-1">Related ID (optional)</label>
          <input
            id="relatedId"
            type="number"
            value={relatedId ?? ''}
            onChange={(e) => setRelatedId(e.target.value ? parseInt(e.target.value) : null)}
            className="w-full border rounded px-3 py-2"
            placeholder="Enter related client/project ID"
            disabled={actionType === 'message_summary'}
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Processing...' : 'Submit'}
        </button>
      </form>

      {error && <p className="mt-4 text-red-600">Error: {error}</p>}

      {response && (
        <div className="mt-4 p-4 bg-gray-100 rounded">
          <h3 className="font-semibold mb-2">AI Response:</h3>
          <pre className="whitespace-pre-wrap">{response.output_text}</pre>
        </div>
      )}
    </div>
  );
};
