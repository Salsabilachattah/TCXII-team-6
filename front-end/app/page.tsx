"use client"; // ⚠️ indispensable pour les hooks
// helper to send ticket data to your AI agent API route (e.g. /api/agent)

export async function sendToAgent(type: string, description: string): Promise<string> {
  try {
    const res = await fetch("http://0.0.0.0:8000/ticket", {

      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ type, description }),
    });

    if (!res.ok) {
      const text = await res.text();
      throw new Error(text || "Agent request failed");
    }

    const data = await res.json();
    // expect the agent response in data.reply or data.response
    return (data.reply ?? data.response ?? JSON.stringify(data)) as string;
  } catch (err) {
    // swallow/log and return friendly message
    // console.error(err);
    return "Sorry, something went wrong contacting the AI agent.";
  }
}
import React, { useState } from "react";

// Composant pour afficher la réponse
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

// Composant formulaire
const TicketForm: React.FC = () => {
  const [type, setType] = useState<"guide" | "policies" | "faq" | "">("");
  const [description, setDescription] = useState<string>("");
  const [response, setResponse] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    const autoResponses: Record<string, string> = {
      guide: "Please check the user guide section for step-by-step instructions.",
      policies: "Our policies are available in the security and privacy documentation.",
      faq: "This question is answered in the FAQ section.",
    };

    setResponse(autoResponses[type] || "Thank you, we will get back to you.");
  };

  return (
    <div style={{ textAlign: "center", marginTop: 40 }}>
      {/* Titre hors container et plus grand */}
      <h1 style={{ fontSize: "2rem", marginBottom: "20px" }}>Ticket Form</h1>

      {/* Container principal */}
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

          <button type="submit" style={styles.button} onClick={() => sendToAgent(type, description)}>
            Send
          </button>
        </form>

        <TicketResponse response={response} />
      </div>
    </div>
  );
};

// Styles
const styles: { [key: string]: React.CSSProperties } = {
  container: {
    width: "400px",
    padding: "30px",
    borderRadius: "20px",
    background: "rgba(30,30,80,0.4)",
    backdropFilter: "blur(10px)",
    textAlign: "center",
    color: "#000",
    margin: "0 auto", // centré
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

// Page principale
const Page: React.FC = () => {
  return <TicketForm />;
};

export default Page;
