import React, { createContext, useContext, useState } from 'react'
const Ctx = createContext(null)
export function FiltersProvider({ children }){
  const [source, setSource] = useState('')
  const [ip, setIp] = useState('')
  const [since, setSince] = useState('')
  return <Ctx.Provider value={{source, setSource, ip, setIp, since, setSince}}>{children}</Ctx.Provider>
}
export function useFilters(){ return useContext(Ctx) || { source:'', setSource:()=>{}, ip:'', setIp:()=>{}, since:'', setSince:()=>{} } }
