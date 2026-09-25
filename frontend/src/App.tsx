import { Route, Routes } from 'react-router-dom'
import ProtectedRoute from './auth/ProtectedRoute'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import SessionFormPage from './pages/SessionFormPage'
import SessionsPage from './pages/SessionsPage'

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route element={<ProtectedRoute />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/sessions" element={<SessionsPage />} />
        <Route path="/sessions/:sessionId" element={<SessionFormPage />} />
      </Route>
    </Routes>
  )
}

export default App
