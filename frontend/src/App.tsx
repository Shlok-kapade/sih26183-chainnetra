import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { TriageQueue } from './pages/TriageQueue';
import { CaseWorkspace } from './pages/Cases/CaseWorkspace';
import { NewCase } from './pages/Cases/NewCase';
import { ModelCenter } from './pages/ModelCenter/ModelCenter';
import { LabelExplorer } from './pages/LabelExplorer';
import { AdminDashboard } from './pages/Admin/AdminDashboard';
import { Login } from './pages/Login';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />

        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="queue" element={<TriageQueue />} />
          <Route path="cases/new" element={<NewCase />} />
          <Route path="cases/:caseId" element={<CaseWorkspace />} />
          <Route path="models" element={<ModelCenter />} />
          <Route path="labels" element={<LabelExplorer />} />
          <Route path="admin" element={<AdminDashboard />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
