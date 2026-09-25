import { Route, Routes } from 'react-router-dom'
import ProtectedRoute from './auth/ProtectedRoute'
import CalendarPage from './pages/CalendarPage'
import DashboardPage from './pages/DashboardPage'
import GoalsPage from './pages/GoalsPage'
import LoginPage from './pages/LoginPage'
import PlanDetailPage from './pages/PlanDetailPage'
import PlansPage from './pages/PlansPage'
import RegisterPage from './pages/RegisterPage'
import SessionFormPage from './pages/SessionFormPage'
import SessionsPage from './pages/SessionsPage'

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route element={<ProtectedRoute />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/sessions" element={<SessionsPage />} />
        <Route path="/sessions/new" element={<SessionFormPage />} />
        <Route path="/sessions/:sessionId" element={<SessionFormPage />} />
        <Route path="/plans" element={<PlansPage />} />
        <Route path="/plans/:planId" element={<PlanDetailPage />} />
        <Route path="/calendar" element={<CalendarPage />} />
        <Route path="/goals" element={<GoalsPage />} />
      </Route>
    </Routes>
  )
}

export default App
