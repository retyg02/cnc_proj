import { useState } from 'react';

interface Machine {
  id: number;
  status: string;
  name: string;
}

interface GCodeUploadProps {
  machines: Machine[];

  onUpload: (machineId: string, file: File) => Promise<void>;
}

export default function GCodeUpload({ machines, onUpload }: GCodeUploadProps) {
  const [selectedMachine, setSelectedMachine] = useState<string>('');
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedMachine || !file) {
      alert('Error: Peak the machine and G-code file!');
      return;
    }

    try {
      setUploading(true);
      await onUpload(selectedMachine, file);
      alert(`${file.name} has successfully uploaded to the machine №${selectedMachine}. The machine is working.`);
      setFile(null);
      setSelectedMachine('');
    } catch (err) {
      alert('Invalid file uploading.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="mx-auto bg-[#111c44] border border-slate-800 p-6 rounded-2xl space-y-6 shadow-xl">
      <div>
        <h2 className="text-xl font-bold text-white">Managing programm download</h2>
        <p className="text-slate-400 text-xs mt-1">
          Файлы будут сохранены в директорию бэкенда `/g-code/` для последующего чтения имитатором ЧПУ.
          Files is going to be saved to the folder /g-code/ to be read by the simulator
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
            Peak the machine:
          </label>
          <select
            value={selectedMachine}
            onChange={(e) => setSelectedMachine(e.target.value)}
            className="w-full bg-[#0b1329] border border-slate-800 rounded-xl p-3 text-slate-200 text-sm focus:outline-none focus:border-indigo-500 cursor-pointer"
          >
            <option value="">-- Machine --</option>
            {machines.map(m => (
              <option key={m.id} value={m.id}>
                {m.name} ({m.status === 'working' ? 'Working' : m.status === 'error' ? 'Error' : 'Idle'})
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
            Programm file (.nc, .gcode):
          </label>
          <input
            type="file"
            accept=".nc,.gcode"
            onChange={(e) => {
              if (e.target.files && e.target.files[0]) {
                setFile(e.target.files[0]);
              }
            }}
            className="w-full bg-[#0b1329] border border-slate-800 rounded-xl p-3 text-slate-400 text-sm file:mr-4 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-bold file:bg-indigo-600 file:text-white hover:file:bg-indigo-700 file:cursor-pointer"
          />
        </div>

        <button
          type="submit"
          disabled={uploading}
          className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-700 text-white font-bold p-3.5 rounded-xl text-sm transition-all active:scale-[0.99] cursor-pointer shadow-md shadow-indigo-950/50"
        >
          {uploading ? 'Data transfering...' : '🚀 Send the programm'}
        </button>
      </form>
    </div>
  );
}
