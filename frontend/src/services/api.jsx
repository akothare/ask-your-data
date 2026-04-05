import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:8000"
});

export const sendMessage = async (query, sessionId) => {
  const response = await API.post("/chat", {
    query: query,
    session_id: sessionId
  });

  return response.data;
};