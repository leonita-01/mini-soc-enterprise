const API = import.meta.env.VITE_API_URL || "http://localhost:8000";
function authHeaders(){
  const key = localStorage.getItem('apiKey') || ''
  const tok = localStorage.getItem('token') || ''
  const h = {}
  if (key) h['X-API-Key'] = key
  if (tok) h['Authorization'] = `Bearer ${tok}`
  return h
}
export async function login(email, password){
  const r = await fetch(`${API}/api/login`, { method:'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({email,password}) })
  return r.json()
}
export async function fetchStats(){
  const r = await fetch(`${API}/api/stats`, { headers: authHeaders() }); return r.json()
}
export async function fetchAlerts(status, ip, since, limit=100, offset=0){
  const url = new URL(`${API}/api/alerts`)
  if(status) url.searchParams.set('status', status)
  if(ip) url.searchParams.set('ip', ip)
  if(since) url.searchParams.set('since', since)
  url.searchParams.set('limit', limit); url.searchParams.set('offset', offset)
  const r = await fetch(url, { headers: authHeaders() }); return r.json()
}
export async function fetchLogs(source, limit=100, offset=0, ip=null, since=null){
  const url = new URL(`${API}/api/logs`)
  if(source) url.searchParams.set('source', source)
  if(ip) url.searchParams.set('ip', ip)
  if(since) url.searchParams.set('since', since)
  url.searchParams.set('limit', limit); url.searchParams.set('offset', offset)
  const r = await fetch(url, { headers: authHeaders() }); return r.json()
}
export async function setAlertStatus(id, status){
  const r = await fetch(`${API}/api/alerts/${id}/status`, { method:'POST', headers: {'Content-Type':'application/json', ...authHeaders()}, body: JSON.stringify({status}) })
  return r.json()
}
export function sseConnect(onMessage){
  const es = new EventSource(`${API}/api/stream`)
  es.onmessage = e => { try{ onMessage(JSON.parse(e.data)) }catch{ } }
  return es
}
