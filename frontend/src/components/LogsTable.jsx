import { useEffect, useState } from 'react'
import { fetchLogs } from '../services/api'
import { useFilters } from '../services/filters'
export default function LogsTable(){
  const [rows, setRows] = useState([])
  const f = useFilters()
  useEffect(()=>{ fetchLogs(f.source, 100, 0, f.ip, f.since).then(setRows)},[f.source, f.ip, f.since])
  return (
    <div style={{marginTop:24}}>
      <h2>Recent Logs</h2>
      <table>
        <thead><tr><th>Time</th><th>Source</th><th>Src IP</th><th>Dest Port</th><th>Status</th><th>Path</th></tr></thead>
        <tbody>{rows.map(r=>(
          <tr key={r.id}>
            <td>{new Date(r.ts).toLocaleString()}</td>
            <td>{r.source_type}</td>
            <td>{r.src_ip}</td>
            <td>{r.dst_port ?? '-'}</td>
            <td>{r.status}</td>
            <td>{r.http_path ?? '-'}</td>
          </tr>
        ))}</tbody>
      </table>
    </div>
  )
}
