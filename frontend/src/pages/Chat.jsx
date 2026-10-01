import { useEffect, useRef, useState } from "react";
 import { useNavigate, useParams } from "react-router-dom";
  import api from "../services/api";






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

useEffect(() => {
 const loadUser = async () => {
 try {
 const response = await api.get("/auth/me/");
 setRole(response.data.role);
  } catch (error) { console.error("USER ERROR:", error);
   setError("Не удалось определить пользователя."); } };
    loadUser(); }, []);
     const loadMessages = async () => { /* * /chat/new — чата ещё нет */
     if (isNewConversation) { setMessages([]);
      setLoading(false); return; }

     try { setLoading(true); setError(""); const response = await api.get( `/conversations/${conversationId}/messages/` ); setMessages(response.data); } catch (error) { console.error("MESSAGES ERROR:", error); if (error.response?.status === 404) { setError("Чат не найден."); } else if (error.response?.status === 401) { setError("Сессия истекла. Войдите снова."); } else { setError("Не удалось загрузить сообщения."); } } finally { setLoading(false); } }; /* * Отмечаем сообщения прочитанными */ const markAsRead = async () => { if (!conversationId || isNewConversation) { return; } try { await api.patch( `/conversations/${conversationId}/read/` ); } catch (error) { console.error("READ ERROR:", error); } }; /* * При открытии чата */ useEffect(() => { if (!conversationId) { return; } loadMessages(); markAsRead(); }, [conversationId]); /* * WebSocket */ useEffect(() => { /* * Для нового чата WebSocket пока не нужен. */ if (!conversationId || isNewConversation) { return; } const ws = new WebSocket( `ws://127.0.0.1:8001/ws/conversation/${conversationId}/` ); wsRef.current = ws; ws.onopen = () => { console.log("WebSocket connected"); }; ws.onmessage = (event) => { try { const data = JSON.parse(event.data); console.log("WS MESSAGE:", data); setMessages((prev) => { const exists = prev.some( (message) => message.id === data.id ); if (exists) { return prev; } return [...prev, data]; }); } catch (error) { console.error( "WebSocket message parse error:", error ); } }; ws.onerror = (error) => { console.error("WebSocket ERROR:", error); }; ws.onclose = () => { console.log("WebSocket disconnected"); }; return () => { ws.close(); wsRef.current = null; }; }, [conversationId]); /* * Отправка сообщения */ const sendMessage = async () => { const text = messageText.trim(); if (!text || sending) { return; } try { setSending(true); setError(""); /* * Админ отправляет через: * /conversations/send/ * * Пациент отправляет через: * /conversations/messages/ */ const endpoint = role === "admin" ? "/conversations/send/" : "/conversations/messages/"; /* * Для нового чата conversation_id отсутствует. */ const data = { content: text, }; /* * Если это уже существующий чат, * передаём его ID. */ if (!isNewConversation) { data.conversation_id = conversationId; } const response = await api.post( endpoint, data ); console.log( "SEND RESPONSE:", response.data ); setMessageText(""); /* * Backend создал новый Conversation * и вернул его ID. */ if ( isNewConversation && response.data.conversation_id ) { navigate( `/chat/${response.data.conversation_id}`, { replace: true, } ); } } catch (error) { console.error("SEND ERROR:", error); if (error.response?.status === 401) { setError( "Сессия истекла. Войдите снова." ); } else if (error.response?.status === 403) { setError( "У вас нет доступа к этому чату." ); } else if (error.response?.status === 404) { setError("Чат не найден."); } else { setError( error.response?.data?.detail || "Не удалось отправить сообщение." ); } } finally { setSending(false); } }; /* * Enter = отправить * Shift + Enter = новая строка */ const handleKeyDown = (event) => { if ( event.key === "Enter" && !event.shiftKey ) { event.preventDefault(); sendMessage(); } }; /* * Загрузка */ if (loading) { return <div>Загрузка...</div>; } return ( <div> <h1> {isNewConversation ? "Новый чат" : "Чат"} </h1> {error && ( <div> <p>{error}</p> </div> )} <div> {messages.length === 0 ? ( <div> <h2> {isNewConversation ? "Начните разговор" : "Сообщений пока нет"} </h2> <p> {isNewConversation ? "Напишите первое сообщение." : "В этом чате пока нет сообщений."} </p> </div> ) : ( messages.map((message) => ( <div key={message.id}> <p> <strong> {message.role} </strong> </p> <p> {message.content} </p> {message.created_at && ( <small> {new Date( message.created_at ).toLocaleString()} </small> )} <hr /> </div> )) )} </div> <div> <textarea value={messageText} onChange={(event) => setMessageText( event.target.value ) } onKeyDown={handleKeyDown} placeholder="Введите сообщение..." disabled={sending} rows={4} /> <br /> <button onClick={sendMessage} disabled={ sending || !messageText.trim() } > {sending ? "Отправка..." : "Отправить"} </button> </div> </div> ); } export default Chat;