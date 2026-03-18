import { cn } from '@/lib/utils';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export function Input({ label, error, className, ...props }: InputProps) {
  return (
    <div className="w-full">
      {label && <label className="block text-sm font-semibold text-gray-700 mb-2">{label}</label>}
      <input
        className={cn(
          'w-full px-4 py-2.5 border-2 border-gray-200 rounded-lg bg-white text-gray-900 placeholder-gray-400 transition-all duration-200 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200',
          error && 'border-red-500 focus:border-red-500 focus:ring-red-200',
          className
        )}
        {...props}
      />
      {error && <p className="text-red-500 text-sm font-medium mt-2">{error}</p>}
    </div>
  );
}
