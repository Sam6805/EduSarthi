import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';

interface ComparisonRow {
  metric: string;
  baseline: number;
  optimized: number;
  unit: string;
}

interface ComparisonTableProps {
  data: ComparisonRow[];
}

export function ComparisonTable({ data }: ComparisonTableProps) {
  return (
    <Card>
      <CardHeader>
        <h3 className="font-bold text-lg text-gray-900">Performance Comparison</h3>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 font-semibold text-gray-900 bg-gray-50">
                  Metric
                </th>
                <th className="text-right py-3 px-4 font-semibold text-gray-900 bg-gray-50">
                  Baseline
                </th>
                <th className="text-right py-3 px-4 font-semibold text-gray-900 bg-gray-50">
                  Optimized
                </th>
                <th className="text-right py-3 px-4 font-semibold text-gray-900 bg-gray-50">
                  Improvement
                </th>
              </tr>
            </thead>
            <tbody>
              {data.map((row, index) => {
                const improvement =
                  row.metric.includes('Token') ||
                  row.metric.includes('Cost') ||
                  row.metric.includes('Time')
                    ? ((row.baseline - row.optimized) / row.baseline) * 100
                    : ((row.optimized - row.baseline) / row.baseline) * 100;

                return (
                  <tr key={index} className="border-b border-gray-200 hover:bg-gray-50">
                    <td className="py-4 px-4 text-gray-900 font-medium">{row.metric}</td>
                    <td className="py-4 px-4 text-right text-gray-700">
                      {row.baseline} {row.unit}
                    </td>
                    <td className="py-4 px-4 text-right text-gray-700 font-semibold">
                      {row.optimized} {row.unit}
                    </td>
                    <td className="py-4 px-4 text-right">
                      <Badge variant="success">{improvement.toFixed(1)}% ↑</Badge>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}
