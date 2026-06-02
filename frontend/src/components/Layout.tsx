import { NavLink, Outlet } from "react-router-dom";

const linkClass = ({ isActive }: { isActive: boolean }) =>
  `px-3 py-2 rounded-md text-sm font-medium transition-colors ${
    isActive ? "bg-blue-600 text-white" : "text-gray-300 hover:bg-gray-700 hover:text-white"
  }`;

export default function Layout() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-gray-900 text-white shadow-lg">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <NavLink to="/" className="text-xl font-bold tracking-tight">
            AIOps Assistant
          </NavLink>
          <nav className="flex gap-2">
            <NavLink to="/" end className={linkClass}>
              New Investigation
            </NavLink>
            <NavLink to="/incidents" className={linkClass}>
              Incidents
            </NavLink>
          </nav>
        </div>
      </header>
      <main className="flex-1 max-w-6xl mx-auto w-full px-4 py-6">
        <Outlet />
      </main>
    </div>
  );
}
