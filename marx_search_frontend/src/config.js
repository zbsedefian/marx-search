const API_BASE_URL =
  process.env.NODE_ENV === "development"
    ? "http://localhost:8000"
    : "http://3.142.200.52";

export default API_BASE_URL;
