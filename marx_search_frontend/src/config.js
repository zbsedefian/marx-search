const API_BASE_URL =
  process.env.NODE_ENV === "development"
    ? "http://localhost:8000"
    : "https://api.marxsearch.org";

export default API_BASE_URL;
