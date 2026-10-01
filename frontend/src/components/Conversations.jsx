
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

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
        return <div>Загрузка...</div>;
    }

    return (
        <div>
            <h1>Conversations</h1>

            {conversations.length === 0 ? (
                <div>
                    <p>У вас пока нет сообщений.</p>

                    <button
                        onClick={() => navigate("/chat/new")}
                    >
                        Начать чат
                    </button>
                </div>
            ) : (
                <>
                    <p>Количество: {conversations.length}</p>

                    {conversations.map((conversation) => (
                        <div
                            key={conversation.id}
                            onClick={() =>
                                navigate(`/chat/${conversation.id}`)
                            }
                            style={{
                                cursor: "pointer",
                                marginBottom: "20px",
                            }}
                        >
                            <h2>
                                {conversation.lead_name || "Без имени"}
                            </h2>

                            <p>
                                {conversation.lead_phone ||
                                    "Без телефона"}
                            </p>

                            <hr />
                        </div>
                    ))}
                </>
            )}
        </div>
    );
}

export default Conversations;

