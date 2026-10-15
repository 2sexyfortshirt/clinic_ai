
import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../services/api";
import AdminChat from "./AdminChat";
import "./AdminChat.css";
import LogoutButton from "../components/LogoutButton";


function AdminConversations() {
    const { conversationId } = useParams();
    const navigate = useNavigate();

    const [conversations, setConversations] = useState([]);
    const [search, setSearch] = useState("");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    // =========================
    // LOAD CONVERSATIONS
    // =========================

    useEffect(() => {
        const loadConversations = async () => {
            try {
                setLoading(true);
                setError("");

                const response = await api.get("/conversations/");

                console.log(
                    "ADMIN CONVERSATIONS:",
                    response.data
                );

                setConversations(response.data);

            } catch (error) {
                console.error(
                    "Conversations error:",
                    error
                );

                setError(
                    "Не удалось загрузить разговоры"
                );

            } finally {
                setLoading(false);
            }
        };

        loadConversations();
    }, []);

    // =========================
    // SEARCH
    // =========================

    const filteredConversations = useMemo(() => {
        const value = search.trim().toLowerCase();

        if (!value) {
            return conversations;
        }

        return conversations.filter((conversation) => {
            const name = (
                conversation.lead_name || ""
            ).toLowerCase();

            const phone = (
                conversation.lead_phone || ""
            ).toLowerCase();

            return (
                name.includes(value) ||
                phone.includes(value)
            );
        });

    }, [conversations, search]);

    // =========================
    // OPEN CONVERSATION
    // =========================

    const openConversation = (id) => {
        navigate(`/admin/conversations/${id}`);
    };

    // =========================
    // BACK
    // =========================

    const backToConversations = () => {
        navigate("/admin/conversations");
    };

    return (


        <div className="admin-conversations">
         <LogoutButton />

            {/* =========================
                SIDEBAR
            ========================= */}

            <aside
                className={`conversations-sidebar ${
                    conversationId
                        ? "sidebar-hidden-mobile"
                        : ""
                }`}
            >

                {/* HEADER */}

                <div className="sidebar-header">

                    <div>
                        <h1>Conversations</h1>

                        <span>
                            {conversations.length} conversations
                        </span>
                    </div>

                </div>


                {/* SEARCH */}

                <div className="search-container">

                    <input
                        type="text"
                        value={search}
                        onChange={(event) =>
                            setSearch(event.target.value)
                        }
                        placeholder="Search patient..."
                    />

                </div>


                {/* ERROR */}

                {error && (
                    <div className="sidebar-error">
                        {error}
                    </div>
                )}


                {/* LOADING */}

                {loading && (
                    <div className="sidebar-loading">
                        Loading conversations...
                    </div>
                )}


                {/* EMPTY */}

                {!loading &&
                    filteredConversations.length === 0 && (
                        <div className="no-conversations">

                            <div className="no-conversations-icon">
                                💬
                            </div>

                            <h3>
                                No conversations
                            </h3>

                            <p>
                                There are no conversations
                                to display.
                            </p>

                        </div>
                    )
                }


                {/* CONVERSATION LIST */}

                {!loading &&
                    filteredConversations.length > 0 && (

                        <div className="conversation-list">

                            {filteredConversations.map(
                                (conversation) => {

                                    const isActive =
                                        String(
                                            conversation.id
                                        ) ===
                                        String(
                                            conversationId
                                        );

                                    const patientName =
                                        conversation.lead_name ||
                                        "Без имени";

                                    const patientPhone =
                                        conversation.lead_phone ||
                                        "Без телефона";

                                    return (
                                        <div
                                            key={conversation.id}
                                            className={`conversation-item ${
                                                isActive
                                                    ? "active"
                                                    : ""
                                            }`}
                                            onClick={() =>
                                                openConversation(
                                                    conversation.id
                                                )
                                            }
                                        >

                                            {/* AVATAR */}

                                            <div className="conversation-avatar">
                                                {patientName
                                                    .charAt(0)
                                                    .toUpperCase()}
                                            </div>


                                            {/* INFO */}

                                            <div className="conversation-info">

                                                <div className="conversation-top">

                                                    <h3>
                                                        {patientName}
                                                    </h3>

                                                </div>

                                                <p>
                                                    {patientPhone}
                                                </p>

                                            </div>

                                        </div>
                                    );
                                }
                            )}

                        </div>
                    )
                }

            </aside>


            {/* =========================
                CHAT
            ========================= */}

            <main
                className={`admin-chat ${
                    conversationId
                        ? "chat-visible-mobile"
                        : ""
                }`}
            >

                {conversationId ? (

                    <div className="chat-wrapper">

                        {/* MOBILE BACK */}

                        <button
                            className="mobile-back-button"
                            onClick={backToConversations}
                        >
                            ← Conversations
                        </button>

                        <AdminChat />

                    </div>

                ) : (

                    <div className="select-conversation">

                        <div className="select-icon">
                            💬
                        </div>

                        <h2>
                            Select a conversation
                        </h2>

                        <p>
                            Choose a patient from the list
                            to start chatting.
                        </p>

                    </div>

                )}

            </main>

        </div>
    );
}

export default AdminConversations;
