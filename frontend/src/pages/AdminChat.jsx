import { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../services/api";
import "./AdminChat.css";

function Chat() {
    const { conversationId } = useParams();

    const [messages, setMessages] = useState([]);
    const [messageText, setMessageText] = useState("");
    const [loading, setLoading] = useState(true);
    const [sending, setSending] = useState(false);
    const [error, setError] = useState("");

    const messagesEndRef = useRef(null);
    const socketRef = useRef(null);

    // =========================
    // LOAD MESSAGES
    // =========================

    const loadMessages = async () => {
        try {
            setLoading(true);
            setError("");

            const response = await api.get(
                `/conversations/${conversationId}/messages/`
            );

            console.log("MESSAGES:", response.data);

            setMessages(response.data);
        } catch (error) {
            console.error("Messages error:", error);
            setError("Не удалось загрузить сообщения");
        } finally {
            setLoading(false);
        }
    };

    // =========================
    // WEBSOCKET
    // =========================

    useEffect(() => {
        if (!conversationId) {
            return;
        }

        const socket = new WebSocket(
            `ws://127.0.0.1:8001/ws/conversation/${conversationId}/`
        );

        socketRef.current = socket;

        socket.onopen = () => {
            console.log("WebSocket connected");
        };

        socket.onmessage = (event) => {
            const message = JSON.parse(event.data);

            console.log("WebSocket message:", message);

            setMessages((previousMessages) => {
                const exists = previousMessages.some(
                    (item) => item.id === message.id
                );

                if (exists) {
                    return previousMessages;
                }

                return [...previousMessages, message];
            });
        };

        socket.onerror = (error) => {
            console.error("WebSocket error:", error);
        };

        socket.onclose = (event) => {
            console.log("CLOSE CODE:", event.code);
            console.log("CLOSE REASON:", event.reason);
        };

        return () => {
            if (
                socket.readyState === WebSocket.OPEN ||
                socket.readyState === WebSocket.CONNECTING
            ) {
                socket.close();
            }

            if (socketRef.current === socket) {
                socketRef.current = null;
            }
        };
    }, [conversationId]);

    // =========================
    // MARK AS READ
    // =========================

    const markAsRead = async () => {
        try {
            await api.patch(
                `/conversations/${conversationId}/read/`
            );

            console.log("Conversation marked as read");
        } catch (error) {
            console.error("Mark as read error:", error);
        }
    };

    // =========================
    // OPEN CONVERSATION
    // =========================

    useEffect(() => {
        if (!conversationId) {
            return;
        }

        loadMessages();
        markAsRead();
    }, [conversationId]);

    // =========================
    // AUTO SCROLL
    // =========================

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({
            behavior: "auto",
        });
    }, [messages]);

    // =========================
    // SEND MESSAGE
    // =========================

    const sendMessage = async (event) => {
        event.preventDefault();

        const text = messageText.trim();

        if (!text || sending) {
            return;
        }

        try {
            setSending(true);
            setError("");

            await api.post(
                "/conversations/send/",
                {
                    conversation_id: conversationId,
                    content: text,
                }
            );

            setMessageText("");
        } catch (error) {
            console.error("Send message error:", error);

            if (error.response) {
                console.error(
                    "Server response:",
                    error.response.data
                );
            }

            setError("Не удалось отправить сообщение");
        } finally {
            setSending(false);
        }
    };

    // =========================
    // ENTER TO SEND
    // =========================

    const handleKeyDown = (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            sendMessage(event);
        }
    };

    // =========================
    // MESSAGE STYLE
    // =========================

    const getMessageClass = (message) => {
        if (message.role === "admin") {
            return "message admin-message";
        }

        if (message.role === "assistant") {
            return "message assistant-message";
        }

        return "message patient-message";
    };

    // =========================
    // ROLE NAME
    // =========================

    const getRoleName = (role) => {
        if (role === "admin") {
            return "You";
        }

        if (role === "assistant") {
            return "AI Assistant";
        }

        return "Patient";
    };

    // =========================
    // TIME
    // =========================

    const formatTime = (date) => {
        if (!date) {
            return "";
        }

        return new Date(date).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
        });
    };

    return (
        <div className="chat-page">

            {/* HEADER */}

            <header className="chat-header">

                <div className="patient-avatar">
                    A
                </div>

                <div className="chat-header-info">
                    <h2>Conversation</h2>
                    <span>Patient conversation</span>
                </div>

                <div className="online-status">
                    <span className="status-dot"></span>
                    Active
                </div>

            </header>

            {/* CHAT BODY */}

            <main className="chat-body">

                {loading && (
                    <div className="loading">
                        Loading messages...
                    </div>
                )}

                {!loading && messages.length === 0 && (
                    <div className="empty-chat">

                        <div className="empty-icon">
                            💬
                        </div>

                        <h3>No messages yet</h3>

                        <p>
                            Start the conversation with the patient.
                        </p>

                    </div>
                )}

                {!loading &&
                    messages.map((message) => (
                        <div
                            key={message.id}
                            className={getMessageClass(message)}
                        >
                            <div className="message-content">

                                <div className="message-top">

                                    <span className="message-role">
                                        {getRoleName(message.role)}
                                    </span>

                                    <span className="message-time">
                                        {formatTime(
                                            message.created_at
                                        )}
                                    </span>

                                </div>

                                <div className="message-text">
                                    {message.content ??
                                        message.text ??
                                        ""}
                                </div>

                                {message.role === "admin" && (
                                    <div className="read-status">
                                        {message.is_read
                                            ? "✓✓ Read"
                                            : "✓ Sent"}
                                    </div>
                                )}

                            </div>
                        </div>
                    ))}

                <div ref={messagesEndRef} />

            </main>

            {/* ERROR */}

            {error && (
                <div className="chat-error">
                    {error}
                </div>
            )}

            {/* INPUT */}

            <form
                className="chat-input-container"
                onSubmit={sendMessage}
            >
                <textarea
                    value={messageText}
                    onChange={(event) =>
                        setMessageText(event.target.value)
                    }
                    onKeyDown={handleKeyDown}
                    placeholder="Write a message..."
                    rows="1"
                    disabled={sending}
                />

                <button
                    type="submit"
                    className="send-button"
                    disabled={
                        sending ||
                        !messageText.trim()
                    }
                >
                    {sending ? "..." : "Send"}
                </button>
            </form>

        </div>
    );
}

export default Chat;