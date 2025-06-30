import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { AIAssistant } from './ai-assistant';

beforeEach(() => {
  jest.resetAllMocks();
});

describe('AIAssistant', () => {
  test('renders AI Assistant form', () => {
    render(<AIAssistant />);
    expect(screen.getByText(/AI Assistant/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Action Type/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Input Text/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Related ID/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Submit/i })).toBeInTheDocument();
  });

  test('allows input changes and submits form successfully', async () => {
    const mockResponse = { output_text: 'Test AI response' };
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      } as Response)
    );

    render(<AIAssistant />);

    fireEvent.change(screen.getByLabelText(/Input Text/i), { target: { value: 'Test input' } });
    fireEvent.click(screen.getByRole('button', { name: /Submit/i }));

    expect(screen.getByRole('button', { name: /Processing.../i })).toBeDisabled();

    await waitFor(() => {
      expect(screen.getByText(/AI Response:/i)).toBeInTheDocument();
      expect(screen.getByText(mockResponse.output_text)).toBeInTheDocument();
    });

    expect(global.fetch).toHaveBeenCalledTimes(1);
  });

  test('handles API error response', async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: false,
      } as Response)
    );

    render(<AIAssistant />);

    fireEvent.change(screen.getByLabelText(/Input Text/i), { target: { value: 'Test input' } });
    fireEvent.click(screen.getByRole('button', { name: /Submit/i }));

    await waitFor(() => {
      expect(screen.getByText(/Error:/i)).toBeInTheDocument();
    });
  });

  test('handles fetch exception', async () => {
    global.fetch = jest.fn(() => Promise.reject(new Error('Network error')));

    render(<AIAssistant />);

    fireEvent.change(screen.getByLabelText(/Input Text/i), { target: { value: 'Test input' } });
    fireEvent.click(screen.getByRole('button', { name: /Submit/i }));

    await waitFor(() => {
      expect(screen.getByText(/Error: Network error/i)).toBeInTheDocument();
    });
  });
});
