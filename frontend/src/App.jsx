import { BrowserRouter, Routes,Route } from "react-router-dom"



import Chat from "./pages/Chat.jsx";
import Conversations from "./components/Conversations.jsx";
import Login from "./pages/Login.jsx";
import AdminConversations from "./pages/AdminConversations.jsx";
import PatientRegister from "./pages/PatientRegister.jsx";

function App() {
  return (
  <BrowserRouter>
  <Routes>
  <Route path="/login" element={<Login />}/>
  <Route path="/conversations" element={<Conversations />}/>
  <Route path="/chat/:conversationId" element= {<Chat />}/>
  <Route path="/admin/conversations" element={<AdminConversations />}/>
  <Route path="/admin/conversations/:conversationId" element={<AdminConversations />}/>
  <Route path="/register/:slug" element={<PatientRegister />}/>
  </Routes>
  </BrowserRouter>


  );
}

export default App;