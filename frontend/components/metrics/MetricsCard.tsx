import { Card, CardContent } from '@/components/ui/Card';

interface MetricsCardProps {
  label: string;
  value: string | number;
  unit?: string;
  improvement?: number;
  icon?: string;
  highlight?: boolean;
}

export function MetricsCard({ label, value, unit, improvement, icon, highlight }: MetricsCardProps) {
  return (
    <Card className={`relative overflow-hidden hover:shadow-premium transition-all duration-300 ${
      highlight ? 'bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-100' : ''
    }`}>
      {highlight && (
        <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-blue-200 to-indigo-200 rounded-full opacity-20 blur-2xl"></div>
      )}
      <CardContent className="pt-8 relative z-10">
        <div className="space-y-4">
          {icon && <div className="text-5xl">{icon}</div>}
          <p className="text-sm font-semibold text-gray-600 uppercase tracking-wide">{label}</p>
          <div className="flex items-baseline gap-2">
            <p className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">{value}</p>
            {unit && <p className="text-lg text-gray-600 font-semibold">{unit}</p>}
          </div>
          {improvement !== undefined && (
            <div className="pt-2">
              <p className="text-sm font-bold text-green-600 flex items-center gap-1">
                <span>↑</span> {improvement.toFixed(1)}% improvement
              </p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
