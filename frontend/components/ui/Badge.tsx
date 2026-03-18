import { cn } from '@/lib/utils';
import { ReactNode } from 'react';

interface BadgeProps {
  children: ReactNode;
  variant?: 'primary' | 'secondary' | 'success' | 'warning';
  className?: string;
}

export function Badge({ children, variant = 'primary', className }: BadgeProps) {
  const variantStyles = {
    primary: 'bg-blue-100 text-blue-800 font-semibold',
    secondary: 'bg-gray-100 text-gray-800 font-semibold',
    success: 'bg-green-100 text-green-800 font-semibold',
    warning: 'bg-yellow-100 text-yellow-800 font-semibold',
  };

  return (
    <span
      className={cn(
        'inline-block px-3 py-1.5 text-sm rounded-full font-medium',
        variantStyles[variant],
        className
      )}
    >
      {children}
    </span>
  );
}
