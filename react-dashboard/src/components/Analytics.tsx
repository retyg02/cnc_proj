interface AnalyticsProps {
    onStopAll: () => void;
    total_count: number;
    error_count: number;
}

export default function Analytics({onStopAll, total_count, error_count}: AnalyticsProps) {
    return (
        <div className="space-y-6">
      <h2 className="text-xl font-bold text-white tracking-tight">
        Dispatcher panel
      </h2>

      
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="bg-[#111c44] border border-slate-800 p-5 rounded-2xl">
          <span className="text-xs text-slate-400 font-bold uppercase tracking-wider block">
            Machines load
          </span>
          <p className="text-2xl font-black text-white mt-1">
            {total_count > 0 ? (((total_count - error_count) / total_count) * 100).toFixed(0) : 0}%
          </p>
          <p className="text-xs text-slate-500 mt-1">Working machines fraction</p>
        </div>

        <div className="bg-[#111c44] border border-slate-800 p-5 rounded-2xl">
          <span className="text-xs text-slate-400 font-bold uppercase tracking-wider block">
            Current incedents or Idle
          </span>
          <p className={`text-2xl font-black mt-1 ${error_count > 0 ? 'text-rose-500' : 'text-emerald-400'}`}>
            {error_count} m.
          </p>
          <p className="text-xs text-slate-500 mt-1">Demand warning</p>
        </div>
      </div>

      
    </div>
    );
}