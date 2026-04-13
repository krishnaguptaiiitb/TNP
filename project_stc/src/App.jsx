import { useState } from 'react'
import {Outlet, Link, BrowserRouter, Routes, Route} from 'react-router-dom'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import Layout from './components/layout'
import Companies from './components/companies'
import Students from './components/students'
import Sessions from './components/sessions'
import YearSession from './components/yearsession'
function App() {
  const [count, setCount] = useState(0)

  return (
    <BrowserRouter>
      <Routes>
        <Route path='/' element={<Layout/>}>
          <Route index element={<Companies/>}/>
          <Route path="companies" element={<Companies/>} />
          <Route path="students" element={<Students />} />
          <Route path="sessions" element={<Sessions />}>
            <Route path=":year" element={<YearSession />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
