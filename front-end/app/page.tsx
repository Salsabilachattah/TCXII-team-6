"use client"; // ⚠️ indispensable pour les hooks

import React, { useState } from "react";

// helper to send ticket data to your AI agent API
async function sendToAgent(type: string, description: string): Promise<string> {
  try {
    const res = await fetch("http://localhost:8000/ticket", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ticket_id: crypto.randomUUID(),
        content: `[${type.toUpperCase()}] ${description}`,
      }),
    });

    if (!res.ok) {
      const text = await res.text();
      throw new Error(text);
    }

    const data = await res.json();
    return data.response ?? "No response from agent";
  } catch {
    return "Backend error";
  }
}


// ================= Response Component =================
type TicketResponseProps = {
  response: string | null;
};

const TicketResponse: React.FC<TicketResponseProps> = ({ response }) => {
  if (!response) return null;

  return (
    <div style={styles.responseBox}>
      <h3>Response</h3>
      <p>{response}</p>
    </div>
  );
};

// ================= Form Component =================
const TicketForm: React.FC = () => {
  const [type, setType] = useState<"guide" | "policies" | "faq" | "">("");
  const [description, setDescription] = useState("");
  const [response, setResponse] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);

    const agentResponse = await sendToAgent(type, description);
    setResponse(agentResponse);

    setLoading(false);
  };

  return (
    <div style={{ textAlign: "center", marginTop: 40 }}>
      {/* Title outside container */}
      <h1 style={{ fontSize: "2rem", marginBottom: 20 }}>Ticket Form</h1>

      <div style={styles.container}>
        <form onSubmit={handleSubmit} style={styles.form}>
          <select
            value={type}
            onChange={(e) => setType(e.target.value as any)}
            required
            style={styles.input}
          >
            <option value="">Type of request</option>
            <option value="guide">Guide</option>
            <option value="policies">Policies</option>
            <option value="faq">FAQ</option>
          </select>

          <textarea
            placeholder="Description of the problem"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
            style={styles.textarea}
          />

          <button type="submit" style={styles.button} disabled={loading}>
            {loading ? "Sending..." : "Send"}
          </button>
        </form>

        <TicketResponse response={response} />
      </div>
    </div>
  );
};

// ================= Styles =================
const styles: { [key: string]: React.CSSProperties } = {
  container: {
    width: "400px",
    padding: "30px",
    borderRadius: "20px",
    background: "rgba(30,30,80,0.4)",
    backdropFilter: "blur(10px)",
    textAlign: "center",
    margin: "0 auto",
  },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: "15px",
  },
  input: {
    padding: "12px",
    borderRadius: "8px",
    border: "none",
    background: "#0a0f3d",
    color: "white",
  },
  textarea: {
    padding: "12px",
    borderRadius: "8px",
    border: "none",
    background: "#0a0f3d",
    color: "white",
    minHeight: "80px",
  },
  button: {
    padding: "12px",
    borderRadius: "8px",
    border: "none",
    background: "#0a0f3d",
    color: "white",
    cursor: "pointer",
  },
  responseBox: {
    marginTop: "20px",
    padding: "15px",
    background: "#0a0f3d",
    color: "white",
    borderRadius: "10px",
  },
};

// ================= Page =================
const Page: React.FC = () => {
  return <TicketForm />;
};

export default Page;
