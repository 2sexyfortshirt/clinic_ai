import { Navigate } from "react-router-dom";

function ProtectedRoute({ children, allowedRole }) {
    const token = localStorage.getItem("access_token");

    if (!token) {
        return <Navigate to="/login" replace />;
    }

    const role = localStorage.getItem("user_role");

    if (allowedRole && role !== allowedRole) {
        return <Navigate to="/conversations" replace />;
    }

    return children;
}

export default ProtectedRoute;