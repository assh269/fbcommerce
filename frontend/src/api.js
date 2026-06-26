import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8001",
  headers: { "Content-Type": "application/json" },
});

export const getSellers = () => api.get("/sellers");
export const getSellerByTelegram = (tgId) => api.get(`/sellers/telegram/${tgId}`);
export const createSeller = (data) => api.post("/sellers", data);

export const getProducts = (params) => api.get("/products", { params });
export const getProduct = (id) => api.get(`/products/${id}`);
export const createProduct = (data, sellerId) =>
  api.post(`/products?seller_id=${sellerId}`, data);
export const updateProduct = (id, data) => api.patch(`/products/${id}`, data);
export const deleteProduct = (id) => api.delete(`/products/${id}`);

export const getOrders = (params) => api.get("/orders", { params });
export const getOrder = (id) => api.get(`/orders/${id}`);
export const updateOrderStatus = (id, status) =>
  api.patch(`/orders/${id}/status`, { status });

export const getCategories = () => api.get("/categories");

export const getReviews = (productId) => api.get(`/reviews/product/${productId}`);

export default api;
