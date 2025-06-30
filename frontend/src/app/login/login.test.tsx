import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import LoginPage from './page';

describe('LoginPage', () => {
  test('renders login form', () => {
    render(<LoginPage />);
    expect(screen.getByText(/Sign in to your account/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Email address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Sign in/i })).toBeInTheDocument();
  });

  test('allows input in email and password fields', () => {
    render(<LoginPage />);
    const emailInput = screen.getByLabelText(/Email address/i);
    const passwordInput = screen.getByLabelText(/Password/i);

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });

    expect(emailInput).toHaveValue('test@example.com');
    expect(passwordInput).toHaveValue('password123');
  });

  test('calls handleSubmit on form submission', () => {
    const consoleSpy = jest.spyOn(console, 'log').mockImplementation(() => {});
    render(<LoginPage />);
    const emailInput = screen.getByLabelText(/Email address/i);
    const passwordInput = screen.getByLabelText(/Password/i);
    const submitButton = screen.getByRole('button', { name: /Sign in/i });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);

    expect(consoleSpy).toHaveBeenCalledWith('Logging in with', {
      email: 'test@example.com',
      password: 'password123',
    });

    consoleSpy.mockRestore();
  });
});
