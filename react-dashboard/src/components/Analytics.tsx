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

      {/* Сетка быстрых отчетов по цеху */}
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
            Current incedents
          </span>
          <p className={`text-2xl font-black mt-1 ${error_count > 0 ? 'text-rose-500' : 'text-emerald-400'}`}>
            {error_count} errors
          </p>
          <p className="text-xs text-slate-500 mt-1">Demand warning</p>
        </div>
      </div>

      <div className="bg-[#111c44] border border-rose-500/20 p-6 rounded-2xl space-y-4 shadow-2xl">
        <div>
          <h3 className="text-lg font-bold text-rose-400 flex items-center gap-2">
            ⚠️ IMPORTANT COMMAND ZONE
          </h3>
          <p className="text-slate-400 text-xs mt-1">
            Taping on the button below is going to send group POST-request through FastAPI to all the active controllers
          </p>
        </div>

        <button 
          onClick={onStopAll}
          className="bg-rose-600 hover:bg-rose-700 text-white font-black text-sm p-5 rounded-xl uppercase tracking-widest transition-all duration-200 active:scale-[0.98] shadow-lg shadow-rose-900/40 w-full cursor-pointer flex items-center justify-center gap-2"
        >
          🚨 TERMINATE ALL MACHINES
        </button>
      </div>
    </div>
    );
}