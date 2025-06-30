/**
 * Input component for Smart CRM SaaS application.
 * A reusable input component with various states and features.
 * Built with Tailwind CSS and supports accessibility features.
 */

import * as React from 'react';
import { cn } from '@/lib/utils';

// Input component props interface
export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  // Additional props specific to our input component
  error?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  label?: string;
  helperText?: string;
}

/**
 * Input component with support for icons, labels, and error states.
 * 
 * @param className - Additional CSS classes
 * @param type - Input type (text, password, email, etc.)
 * @param error - Error message to display
 * @param leftIcon - Icon to display on the left side
 * @param rightIcon - Icon to display on the right side
 * @param label - Input label text
 * @param helperText - Helper text to display below input
 * @param disabled - Disable the input
 * @param props - Additional input props
 */
const Input = React.forwardRef<HTMLInputElement, InputProps>(
  (
    {
      className,
      type = 'text',
      error,
      leftIcon,
      rightIcon,
      label,
      helperText,
      disabled,
      ...props
    },
    ref
  ) => {
    // Generate unique ID for input-label association
    const id = React.useId();

    return (
      <div className="w-full">
        {/* Label */}
        {label && (
          <label
            htmlFor={id}
            className={cn(
              'mb-2 block text-sm font-medium',
              error ? 'text-red-500' : 'text-gray-700'
            )}
          >
            {label}
          </label>
        )}

        {/* Input container */}
        <div className="relative">
          {/* Left icon */}
          {leftIcon && (
            <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-gray-400">
              {leftIcon}
            </div>
          )}

          {/* Input element */}
          <input
            id={id}
            type={type}
            className={cn(
              // Base styles
              'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
              // Icon padding
              leftIcon && 'pl-10',
              rightIcon && 'pr-10',
              // Error styles
              error && 'border-red-500 focus-visible:ring-red-500',
              // Custom classes
              className
            )}
            disabled={disabled}
            aria-invalid={!!error}
            aria-describedby={error ? `${id}-error` : helperText ? `${id}-helper` : undefined}
            ref={ref}
            {...props}
          />

          {/* Right icon */}
          {rightIcon && (
            <div className="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400">
              {rightIcon}
            </div>
          )}
        </div>

        {/* Error message */}
        {error && (
          <p
            id={`${id}-error`}
            className="mt-2 text-sm text-red-500"
            role="alert"
          >
            {error}
          </p>
        )}

        {/* Helper text */}
        {helperText && !error && (
          <p
            id={`${id}-helper`}
            className="mt-2 text-sm text-gray-500"
          >
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export { Input };
