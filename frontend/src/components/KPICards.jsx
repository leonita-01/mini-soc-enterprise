import { useEffect, useState } from 'react'
import { fetchStats } from '../services/api'
export default function KPICards(){
  const [s, setS] = useState(null)
  useEffect(()=>{ fetchStats().then(setS) },[])
  if(!s) return <div>Loading KPIs...</div>
  return (
    <div style={{display:'grid', gridTemplateColumns:'repeat(3, 1fr)', gap:12}}>
      <div className="card">Total Events: <b>{s.total_events}</b></div>
      <div className="card">Total Alerts: <b>{s.total_alerts}</b></div>
      <div className="card">SSH fails (24h): <b>{s.ssh_failed_last_24h}</b></div>
    </div>
  )
}
