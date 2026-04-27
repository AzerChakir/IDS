import React, { useState, useEffect } from 'react';

// Simple SVG Icons
const ShieldAlertIcon = () => <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>;
const ActivityIcon = () => <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>;
const ServerIcon = () => <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" /></svg>;
const ShieldCheckIcon = () => <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>;

function App() {
  const [stats, setStats] = useState({ total_traffic_bytes: 0, blocked_connections: 0, active_threats: 0, system_health: 'Loading' });
  const [alerts, setAlerts] = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  // Use relative path if the app is served via NGINX or same domain
  const API_BASE = "http://localhost:8000/api";

  const loadData = async () => {
    try {
      const statsRes = await fetch(`${API_BASE}/dashboard/stats`);
      const alertRes = await fetch(`${API_BASE}/dashboard/alerts`);
      const histRes = await fetch(`${API_BASE}/dashboard/history`);
      
      if (statsRes.ok) setStats(await statsRes.json());
      if (alertRes.ok) setAlerts(await alertRes.json());
      if (histRes.ok) setHistory(await histRes.json());
      
      setLoading(false);
    } catch (e) {
      console.error("Failed to load dashboard data", e);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000); // Polling every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const handleBlock = (ip) => {
    alert(`Mock: Blocking IP ${ip}`);
    // In real scenario: fetch(`${API_BASE}/responder/block`, { method: 'POST', body: JSON.stringify({ip}) })
  };

  return (
    <div className="min-h-screen bg-dark-900 text-white font-sans p-6">
      <header className="mb-8 flex items-center justify-between border-b border-dark-700 pb-4">
        <div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-brand-400 to-blue-600">PCD IDS</h1>
          <p className="text-sm text-gray-400 mt-1">Network Administrator Dashboard</p>
        </div>
        <div className="flex items-center space-x-3 bg-dark-800 px-4 py-2 rounded-lg border border-dark-700">
          {stats.system_health === "Healthy" ? <ShieldCheckIcon /> : <ShieldAlertIcon />}
          <span className="font-semibold text-sm">Status: {stats.system_health}</span>
        </div>
      </header>

      <main className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Stats Row */}
        <div className="lg:col-span-3 grid grid-cols-1 md:grid-cols-3 gap-6">
          <StatCard title="Total Traffic" value={`${(stats.total_traffic_bytes / 1024).toFixed(2)} KB`} icon={<ActivityIcon />} />
          <StatCard title="Active Threats" value={stats.active_threats} alert={stats.active_threats > 0} icon={<ShieldAlertIcon />} />
          <StatCard title="Blocked Connections" value={stats.blocked_connections} icon={<ServerIcon />} />
        </div>

        {/* Alerts Column */}
        <div className="lg:col-span-1 bg-dark-800 rounded-xl p-5 border border-dark-700 shadow-lg">
          <h2 className="text-xl font-bold mb-4 flex items-center"><ShieldAlertIcon /><span className="ml-2">Recent Alerts</span></h2>
          <div className="space-y-4">
            {loading ? <p className="text-gray-400 animate-pulse">Loading alerts...</p> : alerts.length === 0 ? <p className="text-green-400 text-sm">No active alerts.</p> : null}
            {alerts.map(a => (
              <div key={a.id} className="p-3 bg-red-900/20 border border-red-500/30 rounded-lg">
                <div className="flex justify-between items-start mb-2">
                  <span className="text-red-400 font-bold text-sm tracking-wide">{a.type}</span>
                  <span className="text-xs text-gray-500">{new Date(a.timestamp).toLocaleTimeString()}</span>
                </div>
                <div className="text-sm text-gray-300 mb-3">Source: <span className="font-mono text-gray-100">{a.source_ip}</span></div>
                <button onClick={() => handleBlock(a.source_ip)} className="w-full py-1.5 bg-red-600 hover:bg-red-700 text-xs font-semibold rounded transition duration-200 shadow shadow-red-900/50">
                  Block IP
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* History Column */}
        <div className="lg:col-span-2 bg-dark-800 rounded-xl p-5 border border-dark-700 shadow-lg overflow-hidden flex flex-col">
          <h2 className="text-xl font-bold mb-4 flex items-center"><ActivityIcon /><span className="ml-2">Live Traffic Log</span></h2>
          <div className="overflow-x-auto flex-1">
            <table className="w-full text-left text-sm whitespace-nowrap">
              <thead className="text-gray-400 border-b border-dark-700">
                <tr>
                  <th className="pb-3 font-semibold">Time</th>
                  <th className="pb-3 font-semibold">Source</th>
                  <th className="pb-3 font-semibold">Destination</th>
                  <th className="pb-3 font-semibold">Protocol</th>
                  <th className="pb-3 font-semibold">Size</th>
                  <th className="pb-3 font-semibold text-right">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-dark-700/50">
                {loading && <tr><td colSpan="6" className="py-4 text-center text-gray-500 animate-pulse">Fetching traffic data...</td></tr>}
                {history.map(log => (
                  <tr key={log.id} className="hover:bg-dark-700/30 transition-colors">
                    <td className="py-3 text-gray-400">{new Date(log.timestamp).toLocaleTimeString()}</td>
                    <td className="py-3 font-mono text-xs">{log.source_ip}</td>
                    <td className="py-3 font-mono text-xs text-gray-400">{log.dest_ip}</td>
                    <td className="py-3"><span className="px-2 py-0.5 rounded-full bg-dark-700 text-xs text-gray-300">{log.protocol}</span></td>
                    <td className="py-3 text-gray-400">{log.bytes} B</td>
                    <td className="py-3 text-right">
                      <span className={`px-2 py-1 rounded text-xs font-bold ${log.status === 'BLOCKED' ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'}`}>
                        {log.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
}

function StatCard({ title, value, alert, icon }) {
  return (
    <div className={`bg-dark-800 rounded-xl p-6 border ${alert ? 'border-red-500/50 shadow-[0_0_15px_rgba(239,68,68,0.15)]' : 'border-dark-700'} shadow-lg flex items-center`}>
      <div className={`p-3 rounded-lg ${alert ? 'bg-red-500/20 text-red-500' : 'bg-brand-500/20 text-brand-400'} mr-4`}>
        {icon}
      </div>
      <div>
        <h3 className="text-gray-400 text-sm font-medium mb-1">{title}</h3>
        <p className={`text-3xl font-bold ${alert ? 'text-red-400' : 'text-white'}`}>{value}</p>
      </div>
    </div>
  );
}

export default App;
