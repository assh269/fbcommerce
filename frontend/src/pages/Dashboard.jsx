import { useEffect, useState } from "react";
import { getOrders, getProducts, getSellers } from "../api";

export default function Dashboard() {
  const [stats, setStats] = useState({ sellers: 0, products: 0, orders: 0, revenue: 0 });

  useEffect(() => {
    Promise.all([getSellers(), getProducts(), getOrders()]).then(
      ([sellers, products, orders]) => {
        const orderList = orders.data || [];
        const totalRevenue = orderList
          .filter((o) => o.status === "delivered")
          .reduce((sum, o) => sum + o.total, 0);

        setStats({
          sellers: sellers.data?.length || 0,
          products: products.data?.length || 0,
          orders: orderList.length,
          revenue: totalRevenue,
        });
      }
    );
  }, []);

  const cards = [
    { label: "Active Sellers", value: stats.sellers, color: "bg-blue-500" },
    { label: "Total Products", value: stats.products, color: "bg-green-500" },
    { label: "Total Orders", value: stats.orders, color: "bg-purple-500" },
    { label: "Revenue (MMK)", value: stats.revenue.toLocaleString(), color: "bg-amber-500" },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {cards.map((card) => (
          <div key={card.label} className="bg-white p-6 rounded-xl shadow-sm border">
            <div className={`w-10 h-10 ${card.color} rounded-lg mb-3`} />
            <p className="text-2xl font-bold">{card.value}</p>
            <p className="text-sm text-gray-500">{card.label}</p>
          </div>
        ))}
      </div>

      <div className="bg-white p-6 rounded-xl shadow-sm border">
        <h2 className="font-semibold mb-2">Getting Started</h2>
        <ol className="list-decimal list-inside text-sm text-gray-600 space-y-1">
          <li>Register your shop via the Telegram bot</li>
          <li>Add products in the Products section</li>
          <li>Share your Telegram bot link on Facebook & TikTok</li>
          <li>Orders appear automatically — track them here</li>
        </ol>
      </div>
    </div>
  );
}
