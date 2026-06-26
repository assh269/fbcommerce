import { useEffect, useState } from "react";
import { getOrders, updateOrderStatus } from "../api";

const statusColors = {
  pending: "bg-yellow-100 text-yellow-700",
  confirmed: "bg-blue-100 text-blue-700",
  shipped: "bg-purple-100 text-purple-700",
  delivered: "bg-green-100 text-green-700",
  cancelled: "bg-red-100 text-red-700",
};

const nextStatus = {
  pending: "confirmed",
  confirmed: "shipped",
  shipped: "delivered",
};

export default function Orders() {
  const [orders, setOrders] = useState([]);

  const load = () => getOrders().then((res) => setOrders(res.data || []));
  useEffect(() => { load(); }, []);

  const handleStatus = async (id, status) => {
    await updateOrderStatus(id, status);
    load();
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Orders</h1>
      <div className="space-y-4">
        {orders.map((o) => (
          <div key={o.id} className="bg-white p-4 rounded-xl shadow-sm border">
            <div className="flex justify-between items-start mb-2">
              <div>
                <p className="font-medium">
                  {o.buyer_name || "Anonymous"} —{" "}
                  {o.total.toLocaleString()} MMK
                </p>
                <p className="text-xs text-gray-500">
                  ID: {o.id.slice(0, 8)}... | {new Date(o.created_at).toLocaleDateString()}
                </p>
              </div>
              <span
                className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                  statusColors[o.status] || "bg-gray-100"
                }`}
              >
                {o.status}
              </span>
            </div>
            {o.items?.length > 0 && (
              <div className="text-sm text-gray-600 mb-2">
                {o.items.map((item) => (
                  <span key={item.id} className="mr-3">
                    {item.product_id.slice(0, 8)}... x{item.quantity}
                  </span>
                ))}
              </div>
            )}
            {o.note && (
              <p className="text-xs text-gray-400 mb-2">Note: {o.note}</p>
            )}
            {nextStatus[o.status] && (
              <button
                onClick={() => handleStatus(o.id, nextStatus[o.status])}
                className="text-xs text-primary-600 hover:underline"
              >
                Mark as {nextStatus[o.status]}
              </button>
            )}
            {o.status === "pending" && (
              <button
                onClick={() => handleStatus(o.id, "cancelled")}
                className="text-xs text-red-500 hover:underline ml-3"
              >
                Cancel
              </button>
            )}
          </div>
        ))}
        {orders.length === 0 && (
          <p className="text-center py-8 text-gray-400">No orders yet.</p>
        )}
      </div>
    </div>
  );
}
