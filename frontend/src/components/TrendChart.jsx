import { useEffect, useState } from 'react'
import { fetchLogs } from '../services/api'
import { LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
export default function TrendChart(){
  const [data, setData] = useState([])
  useEffect(()=>{
    fetchLogs('ssh_auth', 300).then(rows=>{
      const buckets = {}
      rows.forEach(r=>{
        if(r.status!=='ssh_failed') return
        const hour = new Date(r.ts); hour.setMinutes(0,0,0)
        const k = hour.toISOString()
        buckets[k] = (buckets[k]||0) + 1
      })
      setData(Object.entries(buckets).sort().map(([k,v])=>({time:k, fails:v})))
    })
  },[])
  return (
    <div style={{marginTop:24}}>
      <h2>SSH Failures (hourly)</h2>
      <div style={{width:'100%', height:260}}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <Line type="monotone" dataKey="fails" />
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" /><YAxis allowDecimals={false}/><Tooltip />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
