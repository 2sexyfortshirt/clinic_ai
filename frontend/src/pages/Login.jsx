import { useState } from "react";
import api from "../services/api";

function Login() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");

    const handleLogin = async (e) => {
        e.preventDefault();

        try {
            const response = await api.post("/auth/login/", {
                username: username,
                password: password,
            });

            console.log("LOGIN DATA:", JSON.stringify(response.data, null, 2));

            localStorage.setItem(
                "access_token",
                response.data.access
            );

            localStorage.setItem(
                "refresh_token",
                response.data.refresh
            );
            const me = await api.get("/auth/me/");
            console.log("ME:", me.data);
            if (me.data.role === "admin") {
            window.location.href = "/admin/conversations";
            } else {
            window.location.href = "/conversations";
        }

            console.log("Token saved!");

        } catch (error) {
            console.error("LOGIN ERROR:", error.response?.data);
        }
    };

    return (
        <form onSubmit={handleLogin}>
            <h2>Login</h2>

            <input
                type="text"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
            />

            <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
            />

            <button type="submit">
                Login
            </button>
        </form>
    );
}

export default Login;