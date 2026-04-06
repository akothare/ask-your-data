import { useState } from "react";
import { sendMessage } from "../services/api";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid,
  BarChart, Bar
} from "recharts";

const Chat = () => {

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sessionId] = useState(() => "session-" + Date.now());

  const handleSend = async () => {

    if (!input.trim()) return;

    const userMessage = { role: "user", text: input };
    setMessages(prev => [...prev, userMessage]);

    try {
      const response = await sendMessage(input, sessionId);

      let aiMessage;

      const res = response.response;

      if (res.type === "text") {
        aiMessage = { role: "ai", type: "text", content: res.content };

      } else if (res.type === "mixed") {
        aiMessage = {
          role: "ai",
          type: "mixed",
          summary: res.summary,
          data: res.data
        };

      } else if (res.type === "table") {
        aiMessage = {
          role: "ai",
          type: "table",
          content: res.data
        };
      }

      setMessages(prev => [...prev, aiMessage]);

    } catch (error) {
      setMessages(prev => [
        ...prev,
        { role: "ai", type: "text", content: "Error connecting to backend" }
      ]);
    }

    setInput("");
  };

  return (
    <div style={styles.container}>

      <h2>AI Database Assistant</h2>

      <div style={styles.chatBox}>
        {messages.map((msg, index) => (
          <div
            key={index}
            style={{
              ...styles.message,
              alignSelf: msg.role === "user" ? "flex-end" : "flex-start",
              background: msg.role === "user" ? "#DCF8C6" : "#F1F0F0"
            }}
          >
            {msg.role === "user" && <span>{msg.text}</span>}

            {msg.role === "ai" && msg.type === "text" && (
              <span>{msg.content}</span>
            )}

            {msg.role === "ai" && msg.type === "table" && (
              <DataTable data={msg.content} />
            )}

            {msg.role === "ai" && msg.type === "chart" && (
              <ChartView data={msg.content} config={msg.chart} />
            )}

            {msg.role === "ai" && msg.type === "mixed" && (
              <>
                <p>{msg.summary}</p>
                <DataTable data={msg.data} />
              </>
            )}

          </div>
        ))}
      </div>

      <div style={styles.inputBox}>
        <input
          style={styles.input}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask something about your database..."
        />
        <button style={styles.button} onClick={handleSend}>
          Send
        </button>
      </div>

    </div>
  );
};


// 🔥 NEW COMPONENT
const DataTable = ({ data }) => {

  if (!data || data.length === 0) {
    return <span>No data found</span>;
  }

  const columns = Object.keys(data[0]);

  return (
    <div style={{ overflowX: "auto" }}>
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

const ChartView = ({ data, config }) => {

  if (!config) return null;

  const { type, x, y } = config;

  if (type === "line") {
    return (
      <LineChart width={500} height={300} data={data}>
        <CartesianGrid stroke="#ccc" />
        <XAxis dataKey={x} />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey={y} />
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
        <Bar dataKey={y} />
      </BarChart>
    );
  }

  return null;
};


const styles = {
  container: {
    width: "700px",
    margin: "50px auto",
    display: "flex",
    flexDirection: "column",
    fontFamily: "Arial"
  },
  chatBox: {
    height: "450px",
    border: "1px solid #ccc",
    padding: "10px",
    overflowY: "auto",
    display: "flex",
    flexDirection: "column",
    gap: "10px"
  },
  message: {
    padding: "10px",
    borderRadius: "8px",
    maxWidth: "90%"
  },
  inputBox: {
    display: "flex",
    marginTop: "10px"
  },
  input: {
    flex: 1,
    padding: "10px"
  },
  button: {
    padding: "10px 20px"
  },

  // 🔥 Table styles
  table: {
    borderCollapse: "collapse",
    width: "100%"
  },
  th: {
    border: "1px solid #ddd",
    padding: "8px",
    background: "#f2f2f2"
  },
  td: {
    border: "1px solid #ddd",
    padding: "8px"
  }
};

export default Chat;