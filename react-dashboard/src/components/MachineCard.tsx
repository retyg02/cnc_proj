interface MachineCardProps {
  id: number;
  name: string;
  status: 'working' | 'idle' | 'error';
  details: string;
  load_percent: number;
  onStop: (id: number) => void;
  onReset: (id: number) => void;
}

export default function MachineCard({ id, name, status, details, load_percent, onStop, onReset }: MachineCardProps) {
  return (
    <div className={`p-5 rounded-2xl bg-[#111c44] border transition-all duration-300 ${
      status === 'error' ? 'border-rose-500/40 bg-rose-950/10' : 'border-slate-800'
    }`}>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-bold text-white">{name}</h3>
        <span className={`px-2 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider ${
          status === 'working' ? 'bg-emerald-500/10 text-emerald-400' :
          status === 'error' ? 'bg-rose-500/10 text-rose-400 animate-pulse' : 'bg-amber-500/10 text-amber-400'
        }`}>
          {status}
        </span>
      </div>

      <div className="mb-4">
        <div className="flex justify-between text-xs text-slate-400 mb-1">
          <span>Load:</span>
          <span className="text-slate-200">{load_percent}%</span>
        </div>
        <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
          <div 
            className={`h-full transition-all duration-500 ${status === 'error' ? 'bg-rose-500' : 'bg-emerald-400'}`}
            style={{ width: `${load_percent}%` }}
          ></div>
        </div>
      </div>

      <p className="text-xs text-slate-400 border-t border-slate-800 pt-3 mb-5 min-h-[32px]">
        {details || 'No data'}
      </p>

            

    </div>
  );
}
