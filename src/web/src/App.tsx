import "./styles/globals.css";
import "./styles/tokens.generated.css";
import { useEffect, useState } from "react";
import { AdminLoginPage } from "./pages/admin/AdminLoginPage";
import { AdminUserManagementPage } from "./pages/admin/AdminUserManagementPage";
import { AdminSession, readAdminSession } from "./pages/admin/adminAuth";
import { Homepage } from "./pages/home/Homepage";

export function App() {
  const [adminSession, setAdminSession] = useState<AdminSession | null>(() => readAdminSession());
  const [routeKey, setRouteKey] = useState(() => `${window.location.pathname}${window.location.hash}`);

  useEffect(() => {
    const syncRoute = () => setRouteKey(`${window.location.pathname}${window.location.hash}`);
    window.addEventListener("popstate", syncRoute);
    window.addEventListener("hashchange", syncRoute);
    return () => {
      window.removeEventListener("popstate", syncRoute);
      window.removeEventListener("hashchange", syncRoute);
    };
  }, []);

  const isAdminRoute = routeKey === "/admin" || routeKey.endsWith("#admin-users");
  if (isAdminRoute) {
    if (!adminSession?.access_token) {
      return <AdminLoginPage onLogin={setAdminSession} />;
    }
    return <AdminUserManagementPage session={adminSession} onLogout={() => setAdminSession(null)} />;
  }
  return <Homepage />;
}
