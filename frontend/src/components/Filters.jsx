import React from 'react'
import { useFilters } from '../services/filters'
export default function Filters(){
  const f = useFilters()
  return (
    <div className="card" style={{display:'flex', gap:8, alignItems:'center', marginBottom:12}}>
      <select value={f.source} onChange={e=>f.setSource(e.target.value)}>
        <option value="">All sources</option>
        <option value="ssh_auth">ssh_auth</option>
        <option value="nginx">nginx</option>
        <option value="apache">apache</option>
        <option value="apache_error">apache_error</option>
        <option value="dns">dns</option>
        <option value="ufw">ufw</option>
      </select>
      <input placeholder="IP" value={f.ip} onChange={e=>f.setIp(e.target.value)} />
      <input placeholder="Since (ISO)" value={f.since} onChange={e=>f.setSince(e.target.value)} />
    </div>
  )
}
