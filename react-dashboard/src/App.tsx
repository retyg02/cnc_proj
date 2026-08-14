import { useState, useEffect } from 'react';

import axios from 'axios';

import MachineCard from './components/MachineCard';
import Analytics from './components/Analytics';
import GCodeUpload from './components/GCodeUpload';

type TabType = 'monitoring' | 'gcode' | 'analytics';

interface Machine {
  id: number;
  name: string;
  status: 'working' | 'idle' | 'error';
  details: string;
  load_percent: number;
  gcode_path: string;
  current_command: 'STOP' | 'RESET' | null;
}

export default function App() {
  const [activeTab, setActiveTab] = useState<TabType>('monitoring');

  const [machines, setMachines] = useState<Machine[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMachines = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:8000/telemetry/machines');

      if (response.data && Array.isArray(response.data)) {
        setMachines(response.data);
      } else if (response.data && response.data.data && Array.isArray(response.data.data)) {
        setMachines(response.data.data);
      } else {
        console.error('Backend has given out the invalid data:', response.data);
      }

      setError(null);
    } catch (err) {
      console.error('FastAPI Error:', err);
      setError('There is no response FastAPI (localhost:8000)');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMachines();

    const interval = setInterval(fetchMachines, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleSendCommand = async (id: number, command: 'STOP' | 'RESET') => {
    try {
      await axios.post(`http://127.0.0.1:8000/telemetry/machines/${id}/set_command`, {
        command: command
      });
      fetchMachines();
    } catch (err) {
      alert(`Invalid command send: ${command}`);
    }
  };

  const totalFleet = machines.length;
  const inProduction = machines.filter(m => m.status === 'working').length;
  const emergencyCount = machines.filter(m => m.status === 'error' || m.status === 'idle').length;

  return (
    <div className="min-h-screen bg-[#0b1329] text-slate-100 font-sans antialiased">
      <header className="bg-[#111c44] border-b border-slate-800 sticky top-0 z-50 px-4 py-4 shadow-xl">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row justify-between items-center gap-4">
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
              <span className="text-emerald-400">⚡</span> Automotization
            </h1>
            <p className="text-xs text-slate-400 mt-0.5"></p>
          </div>

          <div className="flex bg-[#0b1329] p-1 rounded-xl border border-slate-800 w-full sm:w-auto">
            <button
              onClick={() => setActiveTab('monitoring')}
              className={`flex-1 sm:flex-none px-4 py-2 rounded-lg text-xs font-bold uppercase transition-all cursor-pointer ${
                activeTab === 'monitoring' ? 'bg-indigo-600 text-white shadow-lg' : 'text-slate-400'
              }`}
            >
              📊 Observing
            </button>
            <button
              onClick={() => setActiveTab('gcode')}
              className={`flex-1 sm:flex-none px-4 py-2 rounded-lg text-xs font-bold uppercase transition-all cursor-pointer ${
                activeTab === 'gcode' ? 'bg-indigo-600 text-white shadow-lg' : 'text-slate-400'
              }`}
            >
              📁 Download G-code
            </button>
            <button
              onClick={() => setActiveTab('analytics')}
              className={`flex-1 sm:flex-none px-4 py-2 rounded-lg text-xs font-bold uppercase transition-all cursor-pointer ${
                activeTab === 'analytics' ? 'bg-indigo-600 text-white shadow-lg' : 'text-slate-400'
              }`}
            >
              📈 Analytics
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-4 md:p-6 space-y-6">
        
        {error && (
          <div className="bg-rose-500/10 border border-rose-500/30 p-4 rounded-xl text-rose-400 text-sm font-semibold text-center animate-pulse">
            ⚠️ {error}
          </div>
        )}

        <section className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="bg-[#111c44] border border-slate-800 p-5 rounded-2xl flex items-center justify-between">
            <div>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Total</p>
              <h3 className="text-2xl font-extrabold mt-1 text-white">{loading ? '...' : `${totalFleet} m.`}</h3>
            </div>
            <div className="bg-slate-800/80 p-3 rounded-xl text-xl">🏭</div>
          </div>
          
          <div className="bg-[#111c44] border border-slate-800 p-5 rounded-2xl flex items-center justify-between">
            <div>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Working</p>
              <h3 className="text-2xl font-extrabold mt-1 text-emerald-400">
                {loading ? '...' : `${machines.filter(m => m.status === 'working').length} m.`}
              </h3>
            </div>
            <div className="bg-emerald-500/10 p-3 rounded-xl text-xl text-emerald-400">●</div>
          </div>

          <div className="bg-[#111c44] border border-slate-800 p-5 rounded-2xl flex items-center justify-between">
            <div>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Idle and Error</p>
              <h3 className="text-2xl font-extrabold mt-1 text-rose-500">{loading ? '...' : `${emergencyCount} m.`}</h3>
            </div>
            <div className="bg-rose-500/10 p-3 rounded-xl text-xl text-rose-500">🚨</div>
          </div>
        </section>

        {(() => {
          if (loading && machines.length === 0) {
            return <div className="text-center py-12 text-slate-400">Data loading...</div>;
          }

          switch (activeTab) {
            case 'monitoring':
              return (
                <div className="space-y-6">
                  <h2 className="text-lg font-bold text-white">Machines map</h2>
                  <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {machines.map((machine) => (
                      <MachineCard 
                        key={machine.id}
                        name={machine.name}
                        id={machine.id}
                        status={machine.status}
                        details={machine.details}
                        load_percent={machine.load_percent}
                        onStop={(targetId) => handleSendCommand(targetId, 'STOP')}
                        onReset={(targetId) => handleSendCommand(targetId, 'RESET')}
                      />
                    ))}
                  </section>
                </div>
              );
            case 'gcode':
              return (
                <GCodeUpload 
                  machines={machines} 
                  onUpload={async (machineId, file) => {
                    const formData = new FormData();
                    formData.append('file', file);

                    await axios.post(`http://127.0.0.1:8000/telemetry/machines/${machineId}/upload-gcode`, formData, {
                      headers: { 'Content-Type': 'multipart/form-data' }
                    });

                    await axios.post(`http://127.0.0.1:8000/telemetry/machines/${machineId}/set_command`, {
                      command: 'RESET'
                    });

                    fetchMachines(); 
                  }}
                />
              );
            case 'analytics':
              return (
                <Analytics 
                  total_count={totalFleet}
                  error_count={emergencyCount} 
                  onStopAll={async () => {
                    const workingMachines = machines.filter(m => m.status === 'working');
                    for (const m of workingMachines) {
                      await axios.post(`http://127.0.0.1:8000/telemetry/machines/${m.id}/set_command`, { command: 'STOP' });
                    }
                    fetchMachines();
                  }}
                />
              );
            default:
              return null;
          }
        })()}

      </main>
    </div>
  );
}
