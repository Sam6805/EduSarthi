interface LowDataToggleProps {
  enabled: boolean;
  onToggle: (enabled: boolean) => void;
}

export function LowDataToggle({ enabled, onToggle }: LowDataToggleProps) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">Data Mode</label>
      <div className="flex items-center gap-3">
        <button
          onClick={() => onToggle(!enabled)}
          className={`relative inline-flex h-8 w-14 items-center rounded-full transition-colors ${
            enabled ? 'bg-blue-600' : 'bg-gray-300'
          }`}
        >
          <span
            className={`inline-block h-6 w-6 transform rounded-full bg-white transition-transform ${
              enabled ? 'translate-x-7' : 'translate-x-1'
            }`}
          />
        </button>
        <span className="text-sm text-gray-600">
          {enabled ? 'Low Data Mode' : 'Normal Mode'}
        </span>
      </div>
    </div>
  );
}
