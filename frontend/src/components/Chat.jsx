import { useState } from "react";
import { sendMessage } from "../services/api";

const Chat = () => {

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  // 🔥 Persistent session
  const [sessionId] = useState(() => "session-" + Date.now());

  const handleSend = async () => {

    if (!input.trim()) return;

    const userMessage = { role: "user", text: input };

    setMessages(prev => [...prev, userMessage]);

    try {
      const response = await sendMessage(input, sessionId);

      let aiText = "";

      if (response.answer) {
        aiText = response.answer;
      } else if (response.data) {
        aiText = JSON.stringify(response.data, null, 2);
      } else if (response.error) {
        aiText = response.error;
      }

      const aiMessage = { role: "ai", text: aiText };

      setMessages(prev => [...prev, aiMessage]);

    } catch (error) {
      setMessages(prev => [
        ...prev,
        { role: "ai", text: "Error connecting to backend" }
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
            <pre style={{ margin: 0 }}>{msg.text}</pre>
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

const styles = {
  container: {
    width: "600px",
    margin: "50px auto",
    display: "flex",
    flexDirection: "column",
    fontFamily: "Arial"
  },
  chatBox: {
    height: "400px",
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
    maxWidth: "80%"
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
  }
};

export default Chat;