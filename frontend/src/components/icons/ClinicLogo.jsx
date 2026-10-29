import "../ClinicLogo.css";

function ClinicLogo() {
  return (
    <div className="clinic-logo">
      <div className="clinic-logo-icon">
        <svg
          viewBox="0 0 24 24"
          width="28"
          height="28"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1.1-1.1a5.5 5.5 0 0 0-7.8 7.8l1.1 1.1L12 21l7.8-7.5 1.1-1.1a5.5 5.5 0 0 0-.1-7.8Z" />
          <path d="M4.5 12h4l2-3.5 3 7 2-3.5h4" />
        </svg>
      </div>

      <div className="clinic-logo-text">
        <span className="clinic-logo-name">Clinic Name</span>
        <span className="clinic-logo-subtitle">PATIENT CARE</span>
      </div>
    </div>
  );
}

export default ClinicLogo;
