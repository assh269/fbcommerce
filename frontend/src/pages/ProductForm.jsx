import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { createProduct, getCategories, getProduct, updateProduct } from "../api";

export default function ProductForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEdit = Boolean(id);
  const [categories, setCategories] = useState([]);
  const [form, setForm] = useState({
    name: "",
    description: "",
    price: "",
    currency: "MMK",
    stock: "0",
    category_id: "",
  });

  useEffect(() => {
    getCategories().then((res) => setCategories(res.data || []));
    if (id) {
      getProduct(id).then((res) => {
        const p = res.data;
        setForm({
          name: p.name || "",
          description: p.description || "",
          price: String(p.price || ""),
          currency: p.currency || "MMK",
          stock: String(p.stock || "0"),
          category_id: p.category_id || "",
        });
      });
    }
  }, [id]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const payload = {
      ...form,
      price: parseFloat(form.price),
      stock: parseInt(form.stock),
      category_id: form.category_id || null,
    };

    if (isEdit) {
      await updateProduct(id, payload);
    } else {
      const sellerId = prompt("Enter your seller ID (from Telegram)");
      if (!sellerId) return;
      await createProduct(payload, sellerId);
    }
    navigate("/products");
  };

  return (
    <div className="max-w-lg">
      <h1 className="text-2xl font-bold mb-6">{isEdit ? "Edit Product" : "Add Product"}</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Product Name</label>
          <input
            className="w-full px-3 py-2 border rounded-lg text-sm"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Description</label>
          <textarea
            className="w-full px-3 py-2 border rounded-lg text-sm"
            rows={3}
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Price</label>
            <input
              type="number"
              step="0.01"
              className="w-full px-3 py-2 border rounded-lg text-sm"
              value={form.price}
              onChange={(e) => setForm({ ...form, price: e.target.value })}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Currency</label>
            <select
              className="w-full px-3 py-2 border rounded-lg text-sm"
              value={form.currency}
              onChange={(e) => setForm({ ...form, currency: e.target.value })}
            >
              <option>MMK</option>
              <option>USD</option>
              <option>THB</option>
            </select>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Stock</label>
            <input
              type="number"
              className="w-full px-3 py-2 border rounded-lg text-sm"
              value={form.stock}
              onChange={(e) => setForm({ ...form, stock: e.target.value })}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Category</label>
            <select
              className="w-full px-3 py-2 border rounded-lg text-sm"
              value={form.category_id}
              onChange={(e) => setForm({ ...form, category_id: e.target.value })}
            >
              <option value="">No category</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="flex gap-3 pt-2">
          <button
            type="submit"
            className="px-6 py-2 bg-primary-600 text-white rounded-lg text-sm hover:bg-primary-700"
          >
            {isEdit ? "Update" : "Create"}
          </button>
          <button
            type="button"
            onClick={() => navigate("/products")}
            className="px-6 py-2 border rounded-lg text-sm hover:bg-gray-50"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
