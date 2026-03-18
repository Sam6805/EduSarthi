import { cn } from '@/lib/utils';
import { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  className?: string;
}

export function Card({ children, className }: CardProps) {
  return (
    <div
      className={cn(
        'rounded-2xl bg-white border border-gray-100 overflow-hidden transition-all duration-300',
        className
      )}
      style={{
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.03), 0 10px 20px rgba(0, 0, 0, 0.06)',
      }}
    >
      {children}
    </div>
  );
}

export function CardHeader({ children, className }: CardProps) {
  return (
    <div className={cn('px-6 sm:px-8 py-5 border-b border-gray-100', className)}>
      {children}
    </div>
  );
}

export function CardContent({ children, className }: CardProps) {
  return <div className={cn('px-6 sm:px-8 py-6', className)}>{children}</div>;
}

export function CardFooter({ children, className }: CardProps) {
  return (
    <div className={cn('px-6 sm:px-8 py-5 border-t border-gray-100', className)}>
      {children}
    </div>
  );
}
