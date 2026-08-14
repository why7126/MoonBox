import "./styles/globals.css";
import "./styles/tokens.generated.css";
import { useEffect, useState } from "react";
import { AdminSpaceManagementPage } from "./pages/admin/AdminSpaceManagementPage";
import { AdminUserManagementPage } from "./pages/admin/AdminUserManagementPage";
import { ADMIN_SESSION_EVENT, AdminSession, canAccessAdmin, readAdminSession } from "./pages/admin/adminAuth";
import { RequirementCenterPage } from "./pages/catalog/RequirementCenterPage";
import { readFrontendSession } from "./pages/home/frontendSession";
import { Homepage } from "./pages/home/Homepage";

export function App() {
  const [adminSession, setAdminSession] = useState<AdminSession | null>(() => readAdminSession());
  const [routeKey, setRouteKey] = useState(() => `${window.location.pathname}${window.location.hash}`);

  useEffect(() => {
    const syncRoute = () => {
      setAdminSession(readAdminSession());
      setRouteKey(`${window.location.pathname}${window.location.hash}`);
    };
    const syncAdminSession = () => setAdminSession(readAdminSession());
    window.addEventListener("popstate", syncRoute);
    window.addEventListener("hashchange", syncRoute);
    window.addEventListener(ADMIN_SESSION_EVENT, syncAdminSession);
    return () => {
      window.removeEventListener("popstate", syncRoute);
      window.removeEventListener("hashchange", syncRoute);
      window.removeEventListener(ADMIN_SESSION_EVENT, syncAdminSession);
    };
  }, []);

  const isAdminRoute = routeKey === "/admin" || routeKey.endsWith("#admin-users");
  const isAdminSpaceRoute = routeKey === "/admin/spaces" || routeKey.endsWith("#admin-spaces");
  const isFrontendLoginRoute = routeKey === "/login" || routeKey.endsWith("#login");
  const isRequirementCenterRoute =
    routeKey === "/requirements" || routeKey === "/requirement-center" || routeKey.endsWith("#requirement-center");
  if (isFrontendLoginRoute) {
    return <Homepage onAdminLogin={setAdminSession} />;
  }
  if (isRequirementCenterRoute) {
    if (!readFrontendSession()) {
      if (window.location.pathname !== "/login") {
        window.history.replaceState(null, "", "/login");
      }
      return <Homepage />;
    }
    return <RequirementCenterPage />;
  }
  if (isAdminRoute || isAdminSpaceRoute) {
    if (!adminSession?.access_token || !canAccessAdmin(adminSession.user)) {
      if (window.location.pathname !== "/login") {
        window.history.replaceState(null, "", "/login");
      }
      return <Homepage onAdminLogin={setAdminSession} />;
    }
    if (isAdminSpaceRoute) {
      return <AdminSpaceManagementPage session={adminSession} onLogout={() => setAdminSession(null)} />;
    }
    return <AdminUserManagementPage session={adminSession} onLogout={() => setAdminSession(null)} />;
  }
  return <Homepage onAdminLogin={setAdminSession} />;
}
