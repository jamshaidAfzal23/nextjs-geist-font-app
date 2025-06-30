/**
 * Loading components for Smart CRM SaaS application.
 * Provides various loading indicators and skeleton components
 * for better user experience during data fetching.
 */

import * as React from 'react';
import { cn } from '@/lib/utils';

// Loading spinner component props
interface LoadingSpinnerProps extends React.HTMLAttributes<HTMLDivElement> {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  color?: 'primary' | 'secondary' | 'white';
}

/**
 * Loading spinner component with customizable size and color.
 * 
 * @param size - Spinner size variant
 * @param color - Spinner color variant
 * @param className - Additional CSS classes
 * @param props - Additional div props
 */
export const LoadingSpinner = React.forwardRef<HTMLDivElement, LoadingSpinnerProps>(
  ({ size = 'md', color = 'primary', className, ...props }, ref) => {
    const sizeClasses = {
      sm: 'h-4 w-4',
      md: 'h-6 w-6',
      lg: 'h-8 w-8',
      xl: 'h-12 w-12',
    };

    const colorClasses = {
      primary: 'border-blue-600',
      secondary: 'border-gray-600',
      white: 'border-white',
    };

    return (
      <div
        ref={ref}
        className={cn(
          'animate-spin rounded-full border-2 border-t-transparent',
          sizeClasses[size],
          colorClasses[color],
          className
        )}
        {...props}
      />
    );
  }
);
LoadingSpinner.displayName = 'LoadingSpinner';

// Loading overlay component props
interface LoadingOverlayProps {
  isLoading: boolean;
  children: React.ReactNode;
  message?: string;
  className?: string;
}

/**
 * Loading overlay component that covers content while loading.
 * 
 * @param isLoading - Whether to show the loading overlay
 * @param children - Content to overlay
 * @param message - Optional loading message
 * @param className - Additional CSS classes
 */
export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  isLoading,
  children,
  message = 'Loading...',
  className,
}) => {
  return (
    <div className={cn('relative', className)}>
      {children}
      {isLoading && (
        <div className="absolute inset-0 z-50 flex items-center justify-center bg-white/80 backdrop-blur-sm">
          <div className="flex flex-col items-center space-y-4">
            <LoadingSpinner size="lg" />
            <p className="text-sm text-gray-600">{message}</p>
          </div>
        </div>
      )}
    </div>
  );
};

// Page loading component
interface PageLoadingProps {
  message?: string;
}

/**
 * Full page loading component for route transitions.
 * 
 * @param message - Optional loading message
 */
export const PageLoading: React.FC<PageLoadingProps> = ({
  message = 'Loading...',
}) => {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="flex flex-col items-center space-y-4">
        <LoadingSpinner size="xl" />
        <p className="text-lg text-gray-600">{message}</p>
      </div>
    </div>
  );
};

// Skeleton component props
interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  width?: string | number;
  height?: string | number;
  rounded?: boolean;
}

/**
 * Skeleton component for placeholder content while loading.
 * 
 * @param width - Skeleton width
 * @param height - Skeleton height
 * @param rounded - Whether to apply rounded corners
 * @param className - Additional CSS classes
 * @param props - Additional div props
 */
export const Skeleton = React.forwardRef<HTMLDivElement, SkeletonProps>(
  ({ width, height, rounded = true, className, style, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          'animate-pulse bg-gray-200',
          rounded && 'rounded',
          className
        )}
        style={{
          width,
          height,
          ...style,
        }}
        {...props}
      />
    );
  }
);
Skeleton.displayName = 'Skeleton';

// Card skeleton component
export const CardSkeleton: React.FC = () => {
  return (
    <div className="rounded-lg border bg-card p-6 shadow-sm">
      <div className="space-y-4">
        <Skeleton height={24} width="60%" />
        <Skeleton height={16} width="80%" />
        <Skeleton height={16} width="40%" />
        <div className="flex space-x-2">
          <Skeleton height={32} width={80} />
          <Skeleton height={32} width={80} />
        </div>
      </div>
    </div>
  );
};

// Table skeleton component
interface TableSkeletonProps {
  rows?: number;
  columns?: number;
}

/**
 * Table skeleton component for loading table data.
 * 
 * @param rows - Number of skeleton rows
 * @param columns - Number of skeleton columns
 */
export const TableSkeleton: React.FC<TableSkeletonProps> = ({
  rows = 5,
  columns = 4,
}) => {
  return (
    <div className="space-y-3">
      {/* Header skeleton */}
      <div className="flex space-x-4">
        {Array.from({ length: columns }).map((_, index) => (
          <Skeleton key={index} height={20} width="100%" />
        ))}
      </div>
      
      {/* Row skeletons */}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div key={rowIndex} className="flex space-x-4">
          {Array.from({ length: columns }).map((_, colIndex) => (
            <Skeleton key={colIndex} height={16} width="100%" />
          ))}
        </div>
      ))}
    </div>
  );
};

// List skeleton component
interface ListSkeletonProps {
  items?: number;
}

/**
 * List skeleton component for loading list data.
 * 
 * @param items - Number of skeleton items
 */
export const ListSkeleton: React.FC<ListSkeletonProps> = ({ items = 5 }) => {
  return (
    <div className="space-y-3">
      {Array.from({ length: items }).map((_, index) => (
        <div key={index} className="flex items-center space-x-3">
          <Skeleton height={40} width={40} rounded />
          <div className="flex-1 space-y-2">
            <Skeleton height={16} width="60%" />
            <Skeleton height={12} width="40%" />
          </div>
        </div>
      ))}
    </div>
  );
};

// Button loading state
interface LoadingButtonProps {
  isLoading: boolean;
  children: React.ReactNode;
  loadingText?: string;
}

/**
 * Button with loading state that shows spinner and optional loading text.
 * 
 * @param isLoading - Whether button is in loading state
 * @param children - Button content when not loading
 * @param loadingText - Text to show when loading
 */
export const LoadingButton: React.FC<LoadingButtonProps> = ({
  isLoading,
  children,
  loadingText,
}) => {
  return (
    <>
      {isLoading && <LoadingSpinner size="sm" color="white" />}
      {isLoading ? loadingText || children : children}
    </>
  );
};
