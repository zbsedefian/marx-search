const API_BASE_URL =
  process.env.NODE_ENV === "development"
    ? "http://localhost:8000"
    : "http://api.marxsearch.org;";

export default API_BASE_URL;
