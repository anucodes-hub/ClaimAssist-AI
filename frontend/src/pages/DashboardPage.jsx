import { LayoutDashboard, FileText, CheckCircle, Clock } from 'lucide-react';

const stats = [
  { label: "Total Claims", value: "12", icon: <FileText /> },
  { label: "Approved", value: "8", icon: <CheckCircle className="text-success" /> },
  { label: "Pending", value: "3", icon: <Clock className="text-yellow-500" /> },
];

export default function Dashboard() {
  return (
    <div className="flex min-h-screen bg-dark text-white">
      {/* Simple Sidebar */}
      <aside className="w-64 border-r border-border p-6 hidden md:block">
        <div className="text-xl font-bold mb-10 flex items-center gap-2">
           <ShieldCheck className="text-accent" /> ClaimAssist
        </div>
        <nav className="space-y-2">
          <a className="flex items-center gap-3 bg-accent/10 text-accent p-3 rounded-xl"><LayoutDashboard size={20}/> Dashboard</a>
          <a className="flex items-center gap-3 text-gray-500 p-3 hover:bg-surface rounded-xl transition"><FileText size={20}/> My Claims</a>
        </nav>
      </aside>

      <main className="flex-1 p-8">
        <div className="flex justify-between items-center mb-8">
          <h2 className="text-3xl font-bold">Dashboard</h2>
          <button className="bg-accent px-4 py-2 rounded-lg font-medium">+ New Claim</button>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
          {stats.map((s, i) => (
            <div key={i} className="bg-surface p-6 rounded-2xl border border-border">
              <div className="flex justify-between items-center mb-4">
                <span className="text-gray-400">{s.label}</span>
                {s.icon}
              </div>
              <div className="text-3xl font-bold">{s.value}</div>
            </div>
          ))}
        </div>

        {/* Recent Claims Table */}
        <div className="bg-surface rounded-2xl border border-border overflow-hidden">
          <div className="p-6 border-b border-border font-bold">Recent Activities</div>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead className="text-gray-500 text-sm">
                <tr>
                  <th className="p-4">Type</th>
                  <th className="p-4">Amount</th>
                  <th className="p-4">Date</th>
                  <th className="p-4">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {[
                  { type: "Health", amt: "$1,200", date: "Feb 24", status: "Approved" },
                  { type: "Vehicle", amt: "$450", date: "Feb 25", status: "Pending" }
                ].map((row, i) => (
                  <tr key={i} className="hover:bg-white/5 transition">
                    <td className="p-4 font-medium">{row.type}</td>
                    <td className="p-4">{row.amt}</td>
                    <td className="p-4 text-gray-400">{row.date}</td>
                    <td className="p-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-bold ${row.status === 'Approved' ? 'bg-success/20 text-success' : 'bg-yellow-500/20 text-yellow-500'}`}>
                        {row.status}
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

/*export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-black text-white p-8">
      <h1 className="text-4xl font-bold text-blue-500 mb-8">
        Claims Dashboard
      </h1>

      <div className="grid grid-cols-3 gap-6">
        <div className="bg-gray-900 p-6 rounded-lg text-center">
          <h2 className="text-gray-400">Total Claims</h2>
          <p className="text-3xl font-bold">0</p>
        </div>

        <div className="bg-green-900 p-6 rounded-lg text-center">
          <h2 className="text-gray-400">Approved</h2>
          <p className="text-3xl font-bold">0</p>
        </div>

        <div className="bg-yellow-900 p-6 rounded-lg text-center">
          <h2 className="text-gray-400">Pending</h2>
          <p className="text-3xl font-bold">0</p>
        </div>
      </div>
    </div>
  );
}
*/