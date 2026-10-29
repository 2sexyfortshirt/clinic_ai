
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";


import ClinicLogo from './icons/ClinicLogo';
import ChatPlusIcon from './icons/ChatPlusIcon';

function Conversations() {
    const [conversations, setConversations] = useState([]);
    const [loading, setLoading] = useState(true);

    const navigate = useNavigate();

    useEffect(() => {
        const loadConversations = async () => {
            try {
                const response = await api.get("/conversations/");

                console.log("API DATA:", response.data);

                setConversations(response.data);
            } catch (error) {
                console.error("API ERROR:", error);
            } finally {
                setLoading(false);
            }
        };

        loadConversations();
    }, []);

    if (loading) {
        return (
            <div className="conversations-loading">
                Загрузка...
            </div>
        );
    }

    return (
        <div className="conversations-page">
            <div className="conversations-container">

                <div className="conversations-brand">
                  <ClinicLogo />
                </div>

                <header className="conversations-header">
                    <h1>Мои диалоги</h1>

                   <button
                       className="start-chat-button"
                       type='button'
                       onClick={() => navigate("/chat/new")}
                       aria-label='Start a new chat'
                       title='Start a new chat'
                   >
                       <ChatPlusIcon/>
                   </button>

                </header>

                {conversations.length === 0 ? (
                    <div className="empty-conversations">
                        <h2>Пока нет диалогов</h2>

                        <p>
                            Здесь будут отображаться ваши сообщения
                            с клиникой. Вы можете начать новый чат.
                        </p>

                        <button
                          className="start-chat-button"
                          onClick={() => navigate("/chat/new")}
                        >
                          Начать чат
                        </button>
                    </div>
                ) : (
                    <>
                        <p className="conversations-count">
                            Всего диалогов: {conversations.length}
                        </p>

                        <div className="conversations-list">
                            {conversations.map((conversation) => (
                                <div
                                    className="conversation-card"
                                    key={conversation.id}
                                    onClick={() =>
                                        navigate(`/chat/${conversation.id}`)
                                    }
                                    role="button"
                                    tabIndex={0}
                                    onKeyDown={(event) => {
                                        if (
                                            event.key === "Enter" ||
                                            event.key === " "
                                        ) {
                                            event.preventDefault();
                                            navigate(
                                                `/chat/${conversation.id}`
                                            );
                                        }
                                    }}
                                >
                                    <h2>
                                        {conversation.lead_name || "Диалог с клиникой"}
                                    </h2>

                                    <p>
                                        {conversation.lead_phone ||
                                            "Контактный номер не указан"}
                                    </p>

                                    <div className="conversation-divider" />
                                </div>
                            ))}
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}

export default Conversations;