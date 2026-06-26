import { Link } from "react-router-dom";

export default function Landing() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-blue-100">
      <header className="max-w-6xl mx-auto px-4 py-6 flex justify-between items-center">
        <h1 className="text-2xl font-bold text-primary-600">fbtiktokcommerce</h1>
        <div className="flex gap-3">
          <Link
            to="/dashboard"
            className="px-4 py-2 text-sm bg-white rounded-lg shadow-sm border hover:bg-gray-50"
          >
            Seller Dashboard
          </Link>
          <a
            href="https://t.me/your_bot_username"
            target="_blank"
            rel="noopener noreferrer"
            className="px-4 py-2 text-sm bg-primary-600 text-white rounded-lg shadow-sm hover:bg-primary-700"
          >
            Open in Telegram
          </a>
        </div>
      </header>

      <section className="max-w-4xl mx-auto px-4 py-20 text-center">
        <h2 className="text-5xl font-bold text-gray-900 mb-4">
          Organize Myanmar's Social Commerce
        </h2>
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          The unified platform for Facebook sellers & TikTok livestreamers.
          Manage products, track orders, and build trust — all from Telegram + Web.
        </p>
        <div className="flex justify-center gap-4">
          <a
            href="https://t.me/your_bot_username"
            target="_blank"
            rel="noopener noreferrer"
            className="px-8 py-3 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700"
          >
            Start on Telegram
          </a>
          <Link
            to="/dashboard"
            className="px-8 py-3 bg-white text-gray-700 rounded-xl font-medium border hover:bg-gray-50"
          >
            Seller Dashboard
          </Link>
        </div>
      </section>

      <section className="max-w-5xl mx-auto px-4 py-16 grid md:grid-cols-3 gap-6">
        {[
          { title: "Unified Catalog", desc: "List products from Facebook & TikTok in one place", icon: "📦" },
          { title: "Order Tracking", desc: "Auto-capture orders from chat. Know your status.", icon: "📋" },
          { title: "Trust & Reviews", desc: "Build reputation with verified buyer reviews.", icon: "⭐" },
        ].map((item) => (
          <div key={item.title} className="bg-white p-6 rounded-2xl shadow-sm border">
            <div className="text-3xl mb-3">{item.icon}</div>
            <h3 className="font-semibold text-lg mb-1">{item.title}</h3>
            <p className="text-gray-500 text-sm">{item.desc}</p>
          </div>
        ))}
      </section>
    </div>
  );
}
