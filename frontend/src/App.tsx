import { useState } from "react";
import { MonthLoad } from "./pages/MonthLoad";
import { Templates } from "./pages/Templates";
import { Reports } from "./pages/Reports";
import { Movements } from "./pages/Movements";
import { es } from "./i18n/es";

type Tab = "templates" | "monthLoad" | "movements" | "reports";

export function App() {
  const [tab, setTab] = useState<Tab>("templates");

  return (
    <div className="app">
      <nav className="tabs">
        <button
          type="button"
          className={tab === "templates" ? "tab active" : "tab"}
          onClick={() => setTab("templates")}
        >
          {es.tabs.templates}
        </button>
        <button
          type="button"
          className={tab === "monthLoad" ? "tab active" : "tab"}
          onClick={() => setTab("monthLoad")}
        >
          {es.tabs.monthLoad}
        </button>
        <button
          type="button"
          className={tab === "movements" ? "tab active" : "tab"}
          onClick={() => setTab("movements")}
        >
          {es.tabs.movements}
        </button>
        <button
          type="button"
          className={tab === "reports" ? "tab active" : "tab"}
          onClick={() => setTab("reports")}
        >
          {es.tabs.reports}
        </button>
      </nav>

      {tab === "templates" && <Templates />}
      {tab === "monthLoad" && <MonthLoad />}
      {tab === "movements" && <Movements />}
      {tab === "reports" && <Reports />}
    </div>
  );
}
