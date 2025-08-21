import React, { useState, useEffect } from 'react'
import './styles.css'
import Login from './components/Login.jsx'
import KPICards from './components/KPICards.jsx'
import AlertsTable from './components/AlertsTable.jsx'
import LogsTable from './components/LogsTable.jsx'
import TrendChart from './components/TrendChart.jsx'
import Filters from './components/Filters.jsx'
import { sseConnect } from './services/api.js'
export default function App(){
  const [token, setToken] = useState(localStorage.getItem('token') || '')
  const [dark, setDark] = useState(localStorage.getItem('dark')==='1')
  useEffect(()=>{ document.body.className = dark ? 'dark' : ''; localStorage.setItem('dark', dark?'1':'0') }, [dark])
  useEffect(()=>{ if(token) localStorage.setItem('token', token) }, [token])
  if(!token && !localStorage.getItem('apiKey')) return <Login onLogin={setToken} />
  useEffect(()=>{ const s = sseConnect(msg=>{ console.log('SSE', msg) }); return ()=> s && s.close() }, [])
  const logout = ()=>{ localStorage.removeItem('token'); localStorage.removeItem('apiKey'); setToken('') }
  return (
    <div style={{padding:16}}>
      <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
        <h1>Mini SOC Enterprise</h1>
        <div><button onClick={()=>setDark(!dark)} style={{marginRight:8}}>{dark?'Light':'Dark'} mode</button><button onClick={logout}>Logout</button></div>
      </div>
      <Filters />
      <KPICards />
      <TrendChart />
      <AlertsTable />
      <LogsTable />
    </div>
  )
}
