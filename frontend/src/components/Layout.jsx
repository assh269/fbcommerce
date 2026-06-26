import { Link, Outlet, useLocation } from "react-router-dom";

const navItems = [
  { path: "/dashboard", label: "Dashboard", icon: "📊" },
  { path: "/products", label: "Products", icon: "📦" },
  { path: "/orders", label: "Orders", icon: "📋" },
];

export default function Layout() {
  const location = useLocation();

  return (
    <div className="min-h-screen flex">
      <aside className="w-64 bg-white border-r border-gray-200 p-4">
        <div className="mb-8">
          <h1 className="text-xl font-bold text-primary-600">fbtiktokcommerce</h1>
          <p className="text-xs text-gray-500">Seller Dashboard</p>
        </div>
        <nav className="space-y-1">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm ${
                location.pathname === item.path
                  ? "bg-primary-50 text-primary-700 font-medium"
                  : "text-gray-600 hover:bg-gray-50"
              }`}
            >
              <span>{item.icon}</span>
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="mt-auto pt-8">
          <Link
            to="/"
            className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700"
          >
            ← Back to site
          </Link>
        </div>
      </aside>
      <main className="flex-1 p-8 bg-gray-50">
        <Outlet />
      </main>
    </div>
  );
}
