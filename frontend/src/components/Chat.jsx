import { useState, useRef, useEffect } from "react";
import { sendMessage } from "../services/api";

import {
  LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid,
  BarChart, Bar
} from "recharts";

const Chat = () => {

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const [sessionId] = useState(() => "session-" + Date.now());

  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async () => {

    if (!input.trim() || loading) return;

    const userMessage = { role: "user", text: input };
    setMessages(prev => [...prev, userMessage]);

    setInput("");
    setLoading(true);

    try {
      const response = await sendMessage(input, sessionId);
      const res = response.response;

      let aiMessage = {
        role: "ai",
        type: res.type,
        content: res.data || null,
        summary: res.summary || null,
        text: res.text || res.content || null,
        sql: res.sql || null,
        chart: response.chart || null
      };

      setMessages(prev => [...prev, aiMessage]);

    } catch (error) {
      setMessages(prev => [
        ...prev,
        {
          role: "ai",
          type: "text",
          text: "Something went wrong. Please try again."
        }
      ]);
    }

    setLoading(false);
  };

  return (
    <div style={styles.container}>

      <div style={styles.header}>
        AskYourDB
      </div>

      <div style={styles.chatBox}>

        {messages.map((msg, index) => (
          <div
            key={index}
            style={{
              ...styles.messageRow,
              justifyContent: msg.role === "user" ? "flex-end" : "flex-start"
            }}
          >
            <div
              style={{
                ...styles.bubble,
                background: msg.role === "user" ? "#2563eb" : "#1e293b",
                color: "#fff"
              }}
            >

              {/* USER */}
              {msg.role === "user" && <span>{msg.text}</span>}

              {/* AI */}
              {msg.role === "ai" && (
                <>

                  {/* SQL */}
                  {msg.type === "sql" && (
                    <>
                      <p style={styles.text}>{msg.text}</p>
                      <pre style={styles.codeBlock}>
                        {msg.sql}
                      </pre>
                    </>
                  )}

                  {/* TEXT */}
                  {msg.type === "text" && msg.text && (
                    <p style={styles.text}>{msg.text}</p>
                  )}

                  {/* SUMMARY */}
                  {msg.summary && (
                    <p style={styles.summary}>{msg.summary}</p>
                  )}

                  {/* CHART */}
                  {msg.chart &&
                    msg.content &&
                    Array.isArray(msg.content) && (
                      <ChartView data={msg.content} config={msg.chart} />
                    )}

                  {/* TABLE */}
                  {(msg.type === "table" || msg.type === "mixed") && (
                    <DataTable data={msg.content} />
                  )}

                </>
              )}

            </div>
          </div>
        ))}

        {loading && (
          <div style={styles.messageRow}>
            <div style={styles.loadingBubble}>
              Thinking...
            </div>
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      <div style={styles.inputContainer}>
        <input
          style={styles.input}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about your database..."
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
        />
        <button style={styles.button} onClick={handleSend}>
          Send
        </button>
      </div>

    </div>
  );
};


// TABLE
const DataTable = ({ data }) => {

  if (!data || data.length === 0) {
    return <span>No data found</span>;
  }

  const columns = Object.keys(data[0]);

  return (
    <div style={{ overflowX: "auto", marginTop: "10px" }}>
      <table style={styles.table}>
        <thead>
          <tr>
            {columns.map(col => (
              <th key={col} style={styles.th}>{col}</th>
            ))}
          </tr>
        </thead>

        <tbody>
          {data.map((row, i) => (
            <tr key={i}>
              {columns.map(col => (
                <td key={col} style={styles.td}>
                  {String(row[col])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};


// CHART
const ChartView = ({ data, config }) => {

  if (!config) return null;
  if (!data || !Array.isArray(data) || data.length === 0) return null;

  const { type, x, y } = config;

  if (!x || !y || !(x in data[0]) || !(y in data[0])) {
    return null;
  }

  if (type === "line") {
    return (
      <LineChart width={500} height={300} data={data}>
        <CartesianGrid stroke="#ccc" />
        <XAxis dataKey={x} />
        <YAxis />
        <Tooltip />
        <Line dataKey={y} stroke="#2563eb" />
      </LineChart>
    );
  }

  if (type === "bar") {
    return (
      <BarChart width={500} height={300} data={data}>
        <CartesianGrid stroke="#ccc" />
        <XAxis dataKey={x} />
        <YAxis />
        <Tooltip />
        <Bar dataKey={y} fill="#2563eb" />
      </BarChart>
    );
  }

  return null;
};


// STYLES
const styles = {
  container: {
    height: "100vh",
    display: "flex",
    flexDirection: "column",
    background: "#0f172a",
    color: "#fff"
  },
  header: {
    padding: "15px",
    fontSize: "20px",
    textAlign: "center"
  },
  chatBox: {
    flex: 1,
    overflowY: "auto",
    padding: "20px",
    display: "flex",
    flexDirection: "column",
    gap: "15px"
  },
  messageRow: {
    display: "flex"
  },
  bubble: {
    padding: "12px 16px",
    borderRadius: "12px",
    maxWidth: "70%"
  },
  text: {
    margin: 0,
    whiteSpace: "pre-wrap"
  },
  summary: {
    margin: "0 0 8px 0",
    color: "#e2e8f0"
  },
  codeBlock: {
    background: "#020617",
    padding: "12px",
    borderRadius: "8px",
    fontFamily: "monospace"
  },
  loadingBubble: {
    padding: "10px",
    background: "#1e293b",
    borderRadius: "10px"
  },
  inputContainer: {
    display: "flex",
    padding: "15px"
  },
  input: {
    flex: 1,
    padding: "12px"
  },
  button: {
    padding: "12px 20px",
    background: "#2563eb",
    color: "#fff",
    border: "none"
  },
  table: {
    borderCollapse: "collapse",
    width: "100%"
  },
  th: {
    border: "1px solid #334155",
    padding: "8px"
  },
  td: {
    border: "1px solid #334155",
    padding: "8px"
  }
};

export default Chat;