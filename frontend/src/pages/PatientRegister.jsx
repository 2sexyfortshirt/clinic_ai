import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../services/api";
import "./PatientRegister.css";

function PatientRegister() {
    const { slug } = useParams();
    const navigate = useNavigate();

    const [form, setForm] = useState({
        username: "",
        email: "",
        password: "",
        name: "",
        phone: "",
    });

    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleChange = (e) => {
        setForm({
            ...form,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        setError("");
        setLoading(true);

        try {

        console.log("SLUG:", slug);
        console.log("REGISTER URL:", `/auth/patient-register/${slug}/`);

            await api.post(

                `/auth/patient-register/${slug}/`,
                form
            );

            navigate("/login");
        } catch (error) {
            console.error(error);

            if (error.response?.data) {
                setError(
                    JSON.stringify(error.response.data)
                );
            } else {
                setError("Registration failed");
            }
        } finally {
            setLoading(false);
        }
    };

   return (
    <div className="patient-register-page">
        <div className="patient-register-card">
            <h1>Patient Registration</h1>

            <form
                className="patient-register-form"
                onSubmit={handleSubmit}
            >
                <input
                    name="name"
                    placeholder="Name"
                    value={form.name}
                    onChange={handleChange}
                    required
                />

                <input
                    name="phone"
                    placeholder="Phone"
                    value={form.phone}
                    onChange={handleChange}
                    required
                />

                <input
                    name="email"
                    type="email"
                    placeholder="Email"
                    value={form.email}
                    onChange={handleChange}
                />

                <input
                    name="username"
                    placeholder="Username"
                    value={form.username}
                    onChange={handleChange}
                    required
                />

                <input
                    name="password"
                    type="password"
                    placeholder="Password"
                    value={form.password}
                    onChange={handleChange}
                    required
                />

                {error && (
                    <div className="patient-register-error">
                        {error}
                    </div>
                )}

                <button type="submit" disabled={loading}>
                    {loading ? "Creating account..." : "Register"}
                </button>
            </form>
        </div>
    </div>
);
}

export default PatientRegister;