
import { useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import api from "../services/api";
import LogoutButton from "../components/LogoutButton";
import "./Chat.css";

function Chat() {
    const { conversationId } = useParams();
    const navigate = useNavigate();

    const isNewConversation = conversationId === "new";

    const [messages, setMessages] = useState([]);
    const [messageText, setMessageText] = useState("");
    const [loading, setLoading] = useState(true);
    const [sending, setSending] = useState(false);
    const [error, setError] = useState("");
    const [role, setRole] = useState(null);

    const wsRef = useRef(null);

    // =========================
    // LOAD CURRENT USER
    // =========================

    useEffect(() => {
        let cancelled = false;

        const loadUser = async () => {
            try {
                const response = await api.get("/auth/me/");

                if (!cancelled) {
                    setRole(response.data.role);
                    localStorage.setItem(
                        "user_role",
                        response.data.role
                    );
                }
            } catch (error) {
                console.error("USER ERROR:", error);

                if (!cancelled) {
                    setError(
                        error.response?.status === 401
                            ? "Сессия истекла. Войдите снова."
                            : "Не удалось определить пользователя."
                    );
                }
            }
        };

        loadUser();

        return () => {
            cancelled = true;
        };
    }, []);

    // =========================
    // LOAD MESSAGES
    // =========================

    useEffect(() => {
        let cancelled = false;

        const loadMessages = async () => {
            if (!conversationId) {
                setLoading(false);
                return;
            }

            if (isNewConversation) {
                setMessages([]);
                setLoading(false);
                return;
            }

            try {
                setLoading(true);
                setError("");

                const response = await api.get(
                    `/conversations/${conversationId}/messages/`
                );

                if (!cancelled) {
                    setMessages(response.data);
                }
            } catch (error) {
                console.error("MESSAGES ERROR:", error);

                if (!cancelled) {
                    if (error.response?.status === 401) {
                        setError(
                            "Сессия истекла. Войдите снова."
                        );
                    } else if (
                        error.response?.status === 403 ||
                        error.response?.status === 404
                    ) {
                        setError(
                            "Чат не найден или у вас нет доступа."
                        );
                    } else {
                        setError(
                            "Не удалось загрузить сообщения."
                        );
                    }
                }
            } finally {
                if (!cancelled) {
                    setLoading(false);
                }
            }
        };

        loadMessages();

        return () => {
            cancelled = true;
        };
    }, [conversationId, isNewConversation]);

    // =========================
    // MARK AS READ
    // =========================

    useEffect(() => {
        if (
            !conversationId ||
            isNewConversation
        ) {
            return;
        }

        const markAsRead = async () => {
            try {
                await api.patch(
                    `/conversations/${conversationId}/read/`
                );
            } catch (error) {
                console.error("READ ERROR:", error);
            }
        };

        markAsRead();
    }, [conversationId, isNewConversation]);

    // =========================
    // WEBSOCKET
    // =========================

    useEffect(() => {
        if (
            !conversationId ||
            isNewConversation
        ) {
            return;
        }

        const token = localStorage.getItem("access_token");

        if (!token) {
            setError("Сессия истекла. Войдите снова.");
            return;
        }
        const wsBase =
  import.meta.env.VITE_WS_URL ||
  "ws://127.0.0.1:8001";

        const ws = new WebSocket(
            `ws://127.0.0.1:8001/ws/conversation/${conversationId}/?token=${encodeURIComponent(token)}`
        );

        wsRef.current = ws;

        ws.onopen = () => {
            console.log("WebSocket connected");
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);

                console.log("WS MESSAGE:", data);

                setMessages((previousMessages) => {
                    const exists = previousMessages.some(
                        (message) => message.id === data.id
                    );

                    if (exists) {
                        return previousMessages;
                    }

                    return [...previousMessages, data];
                });
            } catch (error) {
                console.error(
                    "WebSocket message parse error:",
                    error
                );
            }
        };

        ws.onerror = (error) => {
            console.error("WebSocket ERROR:", error);
        };

        ws.onclose = (event) => {
            console.log(
                "WebSocket disconnected:",
                event.code,
                event.reason
            );
        };

        return () => {
            if (
                ws.readyState === WebSocket.OPEN ||
                ws.readyState === WebSocket.CONNECTING
            ) {
                ws.close();
            }

            if (wsRef.current === ws) {
                wsRef.current = null;
            }
        };
    }, [conversationId, isNewConversation]);

    // =========================
    // SEND MESSAGE
    // =========================

    const sendMessage = async () => {
        const text = messageText.trim();

        if (!text || sending) {
            return;
        }

        if (!role) {
            setError("Определяем пользователя. Попробуйте ещё раз.");
            return;
        }

        try {
            setSending(true);
            setError("");

            const endpoint =
                role === "admin"
                    ? "/conversations/send/"
                    : "/conversations/messages/";

            const data = {
                content: text,
            };

            if (!isNewConversation) {
                data.conversation_id = conversationId;
            }

            const response = await api.post(endpoint, data);

            console.log("SEND RESPONSE:", response.data);

            setMessageText("");

            // Для нового чата backend должен вернуть ID
            // созданного разговора.
            if (
                isNewConversation &&
                response.data.conversation_id
            ) {
                navigate(
                    `/chat/${response.data.conversation_id}`,
                    { replace: true }
                );
                return;
            }

            // Если сообщение не приходит через WebSocket,
            // обновляем список через API.
            if (!isNewConversation) {
                const messagesResponse = await api.get(
                    `/conversations/${conversationId}/messages/`
                );

                setMessages(messagesResponse.data);
            }
        } catch (error) {
            console.error("SEND ERROR:", error);

            if (error.response?.status === 401) {
                setError("Сессия истекла. Войдите снова.");
            } else if (
                error.response?.status === 403 ||
                error.response?.status === 404
            ) {
                setError("У вас нет доступа к этому чату.");
            } else {
                setError(
                    error.response?.data?.detail ||
                    "Не удалось отправить сообщение."
                );
            }
        } finally {
            setSending(false);
        }
    };

    // =========================
    // ENTER TO SEND
    // =========================

    const handleKeyDown = (event) => {
        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {
            event.preventDefault();
            sendMessage();
        }
    };

    // =========================
    // LOADING
    // =========================

    if (loading) {
        return <div>Загрузка...</div>;
    }

    // =========================
    // RENDER
    // =========================

    return (
        <div className="chat-page">
            <header className="chat-header">
                <div className="chat-header-info">
                    <h2>
                        {isNewConversation
                            ? "Новый чат"
                            : "Чат"}
                    </h2>

                    <span>
                        {role === "admin"
                            ? "Администратор"
                            : "Пациент"}
                    </span>
                </div>

                <LogoutButton />
            </header>

            <main className="chat-body">
                {error && (
                    <div className="chat-error">
                        {error}
                    </div>
                )}

                {messages.length === 0 ? (
                    <div className="empty-chat">
                        <h3>
                            {isNewConversation
                                ? "Начните разговор"
                                : "Сообщений пока нет"}
                        </h3>

                        <p>
                            {isNewConversation
                                ? "Напишите первое сообщение."
                                : "В этом чате пока нет сообщений."}
                        </p>
                    </div>
                ) : (
                    messages.map((message) => (
                        <div
                            key={message.id}
                            className={`message ${
                                message.role === "admin"
                                    ? "admin-message"
                                    : message.role === "assistant"
                                      ? "assistant-message"
                                      : "patient-message"
                            }`}
                        >
                            <div className="message-content">
                                <strong>
                                    {message.role === "admin"
                                        ? "Администратор"
                                        : message.role === "assistant"
                                          ? "AI Assistant"
                                          : "Пациент"}
                                </strong>

                                <p>
                                    {message.content ??
                                        message.text ??
                                        ""}
                                </p>

                                {message.created_at && (
                                    <small>
                                        {new Date(
                                            message.created_at
                                        ).toLocaleString()}
                                    </small>
                                )}
                            </div>
                        </div>
                    ))
                )}
            </main>

            <form
                className="chat-input-container"
                onSubmit={(event) => {
                    event.preventDefault();
                    sendMessage();
                }}
            >
                <textarea
                    value={messageText}
                    onChange={(event) =>
                        setMessageText(event.target.value)
                    }
                    onKeyDown={handleKeyDown}
                    placeholder="Введите сообщение..."
                    disabled={sending}
                    rows={3}
                />

                <button
                    type="submit"
                    disabled={
                        sending ||
                        !messageText.trim() ||
                        !role
                    }
                >
                    {sending
                        ? "Отправка..."
                        : "Отправить"}
                </button>
            </form>
        </div>
    );
}

export default Chat;

