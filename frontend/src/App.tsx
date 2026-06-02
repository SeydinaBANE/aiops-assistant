import { Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import IncidentDetail from "./pages/IncidentDetail";
import IncidentsList from "./pages/IncidentsList";
import NewInvestigation from "./pages/NewInvestigation";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<NewInvestigation />} />
        <Route path="incidents" element={<IncidentsList />} />
        <Route path="incidents/:id" element={<IncidentDetail />} />
      </Route>
    </Routes>
  );
}
