import { useEffect, useState } from 'react'
import { fetchAlerts, setAlertStatus } from '../services/api'
export default function AlertsTable(){
  const [rows, setRows] = useState([])
  useEffect(()=>{ fetchAlerts().then(setRows)},[])
  const ack = async (id)=>{ await setAlertStatus(id,'ack'); setRows(r=>r.map(x=>x.id===id?{...x,status:'ack'}:x)) }
  return (
    <div style={{marginTop:24}}>
      <h2>Alerts</h2>
      <table>
        <thead><tr><th>ID</th><th>Time</th><th>Type</th><th>Severity</th><th>Src IP</th><th>Status</th><th>Incident</th><th>Action</th></tr></thead>
        <tbody>{rows.map(r=>(
          <tr key={r.id}>
            <td>{r.id}</td><td>{new Date(r.ts).toLocaleString()}</td>
            <td>{r.type}</td><td>{r.severity}</td><td>{r.src_ip}</td>
            <td>{r.status}</td><td>{r.incident_id ?? '-'}</td>
            <td>{r.status==='open' && <button onClick={()=>ack(r.id)}>Ack</button>}</td>
          </tr>
        ))}</tbody>
      </table>
    </div>
  )
}
