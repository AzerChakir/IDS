import React, { useState } from "react";
import { Search, Download, ChevronLeft, ChevronRight } from "lucide-react";
import { trafficLogs } from "../data/mockData";
import "./History.css";

const PAGE_SIZE = 15;

export default function History() {
  const [searchTerm, setSearchTerm] = useState("");
  const [protocolFilter, setProtocolFilter] = useState("ALL");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [page, setPage] = useState(1);

  const filtered = trafficLogs.filter((log) => {
    if (protocolFilter !== "ALL" && log.protocol !== protocolFilter) return false;
    if (statusFilter !== "ALL" && log.status !== statusFilter) return false;
    if (searchTerm) {
      const s = searchTerm.toLowerCase();
      return log.source_ip.includes(s) || log.dest_ip.includes(s);
    }
    return true;
  });

  const totalPages = Math.ceil(filtered.length / PAGE_SIZE);
  const paginated = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  return (
    <div className="history-page">
      <div className="history-page__header">
        <div>
          <h1 className="history-page__title">Traffic History</h1>
          <p className="history-page__subtitle">{filtered.length} events logged</p>
        </div>
        <button className="history-page__export">
          <Download size={16} /> Export CSV
        </button>
      </div>

      <div className="history-page__filters">
        <div className="history-page__search">
          <Search size={16} />
          <input
            type="text"
            placeholder="Search by IP address..."
            value={searchTerm}
            onChange={(e) => { setSearchTerm(e.target.value); setPage(1); }}
          />
        </div>
        <select value={protocolFilter} onChange={(e) => { setProtocolFilter(e.target.value); setPage(1); }}>
          <option value="ALL">All Protocols</option>
          <option value="TCP">TCP</option>
          <option value="UDP">UDP</option>
          <option value="HTTP">HTTP</option>
          <option value="HTTPS">HTTPS</option>
          <option value="DNS">DNS</option>
          <option value="ICMP">ICMP</option>
          <option value="SSH">SSH</option>
        </select>
        <select value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}>
          <option value="ALL">All Status</option>
          <option value="ALLOWED">Allowed</option>
          <option value="BLOCKED">Blocked</option>
        </select>
      </div>

      <div className="history-page__table-wrap">
        <table className="history-page__table">
          <thead>
            <tr>
              <th>Time</th>
              <th>Source IP</th>
              <th>Destination IP</th>
              <th>Protocol</th>
              <th>Port</th>
              <th>Size</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {paginated.map((log) => (
              <tr key={log.id}>
                <td className="history-page__time">
                  {new Date(log.timestamp).toLocaleString([], {
                    month: "short", day: "numeric", hour: "2-digit", minute: "2-digit",
                  })}
                </td>
                <td className="history-page__ip">{log.source_ip}</td>
                <td className="history-page__ip history-page__ip--dest">{log.dest_ip}</td>
                <td>
                  <span className="history-page__protocol">{log.protocol}</span>
                </td>
                <td className="history-page__port">{log.port}</td>
                <td className="history-page__size">{log.bytes} B</td>
                <td>
                  <span className={`history-page__status ${log.status === "BLOCKED" ? "history-page__status--blocked" : "history-page__status--allowed"}`}>
                    {log.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="history-page__pagination">
        <button disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
          <ChevronLeft size={16} />
        </button>
        <span>Page {page} of {totalPages}</span>
        <button disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>
          <ChevronRight size={16} />
        </button>
      </div>
    </div>
  );
}
