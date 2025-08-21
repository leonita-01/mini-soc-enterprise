import React, { useState } from 'react'
import { login } from '../services/api'
export default function Login({ onLogin }){
  const [email, setEmail] = useState('admin@example.com')
  const [password, setPassword] = useState('ChangeMe!123')
  const [apikey, setApikey] = useState('')
  const submit = async (e)=>{
    e.preventDefault()
    if(apikey){ localStorage.setItem('apiKey', apikey.trim()); onLogin(''); return }
    const res = await login(email, password)
    if(res?.token){ onLogin(res.token) }
  }
  return (
    <div style={{display:'grid', placeItems:'center', minHeight:'100vh'}}>
      <form onSubmit={submit} className="card" style={{width:380}}>
        <h2>Login</h2>
        <p style={{fontSize:12, opacity:.7}}>Login with email/password or paste an API key.</p>
        <input placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} />
        <input placeholder="Password" type="password" value={password} onChange={e=>setPassword(e.target.value)} style={{marginTop:8}} />
        <div style={{marginTop:8, fontSize:12, opacity:.7}}>or</div>
        <input placeholder="API Key (X-API-Key)" value={apikey} onChange={e=>setApikey(e.target.value)} style={{marginTop:8}} />
        <button type="submit" style={{marginTop:12, width:'100%'}}>Continue</button>
      </form>
    </div>
  )
}
