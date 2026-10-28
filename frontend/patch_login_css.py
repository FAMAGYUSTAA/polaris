import os
import sys

css_content = """/* login.css */
.login-page-container {
    min-height: 100vh;
    width: 100vw;
    display: flex;
    flex-direction: column;
    position: relative;
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    overflow: hidden;
    margin: 0;
    box-sizing: border-box;
}

.login-background {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: url('/bg-station.jpg');
    background-size: cover;
    background-position: center bottom;
    background-repeat: no-repeat;
    z-index: 0;
    animation: slow-pan 30s ease-in-out infinite alternate;
}

@keyframes slow-pan {
    0% { transform: scale(1); }
    100% { transform: scale(1.05); }
}

@media (prefers-reduced-motion) {
    .login-background { animation: none; }
    .fade-up, .fade-in, .slide-in { animation: none !important; opacity: 1 !important; transform: none !important; }
    .login-form .input-group, .signin-btn, .offline-divider, .offline-btn, .security-text {
        animation: none !important;
        opacity: 1 !important;
    }
}

.login-overlay {
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.4) 0%, rgba(255,255,255,0.05) 50%, rgba(0,0,0,0.1) 100%);
    z-index: 1;
}

.login-header {
    position: relative;
    z-index: 2;
    display: flex;
    justify-content: space-between;
    padding: 1.5rem 3rem;
    align-items: flex-start;
}

.moes-brand {
    display: flex;
    align-items: center;
    gap: 1rem;
    color: #0f172a;
}

.moes-emblem-placeholder {
    width: 45px;
    height: 55px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #0f172a;
}

.moes-text {
    display: flex;
    flex-direction: column;
    font-weight: 500;
    font-size: 0.9rem;
    line-height: 1.3;
}

.moes-text .hindi {
    font-weight: 700;
    font-size: 1rem;
}

.ncpor-brand {
    display: flex;
    align-items: center;
    gap: 1rem;
    color: #ffffff;
    text-shadow: 0 1px 3px rgba(0,0,0,0.4);
}

.ncpor-logo-img {
    width: 65px;
    height: 65px;
    border-radius: 50%;
    border: 2px solid rgba(255,255,255,0.9);
    box-shadow: 0 2px 6px rgba(0,0,0,0.2);
}

.ncpor-text {
    display: flex;
    flex-direction: column;
}

.ncpor-text .acronym {
    font-size: 1.7rem;
    font-weight: 700;
    letter-spacing: 1px;
    line-height: 1.1;
}

.ncpor-text .full {
    font-size: 0.8rem;
    font-weight: 500;
    letter-spacing: 0.5px;
}

.ncpor-text .tagline {
    font-size: 0.65rem;
    letter-spacing: 1.5px;
    margin-top: 0.2rem;
    opacity: 0.9;
    text-transform: uppercase;
}

.login-main-content {
    flex: 1;
    display: flex;
    align-items: center;
    position: relative;
    z-index: 2;
    padding: 0 5%;
}

.promo-section {
    flex: 1;
    color: #0f172a;
    padding-left: 3rem;
    max-width: 500px;
    animation: fade-in-left 1s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
}

.tricolor-line {
    height: 4px;
    width: 65px;
    background: linear-gradient(to right, #FF9933 33%, #FFFFFF 33%, #FFFFFF 66%, #138808 66%);
    margin-bottom: 0.5rem;
    border-radius: 2px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.promo-subtitle {
    font-size: 0.9rem;
    font-weight: 700;
    letter-spacing: 4px;
    color: #1e3a8a;
    margin-bottom: 1rem;
    text-transform: uppercase;
}

.promo-headline {
    font-size: 3.8rem;
    font-weight: 800;
    line-height: 1.15;
    color: #0f172a;
    margin-bottom: 1.5rem;
}

.promo-footer {
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: 3px;
    color: #334155;
    word-spacing: 8px;
}

.login-card-container {
    width: 440px;
    margin: 0 auto;
    position: relative;
    transform: translateY(-20px);
}

.login-card {
    background: rgba(248, 250, 252, 0.85);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.6);
    border-radius: 12px;
    padding: 2.5rem 2.5rem;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    animation: fade-up 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
}

.login-card-header {
    text-align: center;
    margin-bottom: 2rem;
}

.login-card-header .small-brand {
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 4px;
    color: #475569;
    margin-bottom: 0.5rem;
    text-transform: uppercase;
}

.login-card-header h2 {
    font-size: 1.6rem;
    font-weight: 800;
    color: #0f172a;
    margin: 0 0 0.5rem;
}

.login-card-header .subtitle {
    font-size: 0.95rem;
    color: #475569;
    margin: 0;
}

.login-form .input-group {
    margin-bottom: 1.2rem;
    animation: fade-in 0.6s ease-out forwards;
    opacity: 0;
}

.login-form .input-group:nth-child(1) { animation-delay: 0.1s; }
.login-form .input-group:nth-child(2) { animation-delay: 0.2s; }
.login-form .input-group:nth-child(3) { animation-delay: 0.3s; }
.login-form .input-group:nth-child(4) { animation-delay: 0.4s; }

.login-form label {
    display: block;
    font-size: 0.85rem;
    font-weight: 600;
    color: #475569;
    margin-bottom: 0.4rem;
}

.input-wrapper {
    position: relative;
    display: flex;
    align-items: center;
}

.input-icon {
    position: absolute;
    left: 14px;
    color: #64748b;
    width: 18px;
    height: 18px;
    pointer-events: none;
}

.login-input {
    width: 100%;
    box-sizing: border-box;
    padding: 0.75rem 0.75rem 0.75rem 2.8rem;
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    font-size: 0.95rem;
    color: #0f172a;
    transition: all 0.2s ease;
    font-family: inherit;
}

.login-input:focus {
    outline: none;
    border-color: #1e3a8a;
    box-shadow: 0 0 0 3px rgba(30, 58, 138, 0.15);
}

.login-select {
    appearance: none;
    cursor: pointer;
}

.select-arrow {
    position: absolute;
    right: 14px;
    color: #64748b;
    width: 18px;
    height: 18px;
    pointer-events: none;
}

.password-toggle {
    position: absolute;
    right: 12px;
    background: none;
    border: none;
    color: #64748b;
    cursor: pointer;
    padding: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.password-toggle:focus-visible {
    outline: 2px solid #1e3a8a;
    border-radius: 4px;
}

.signin-btn {
    width: 100%;
    padding: 0.85rem;
    background: #1e3a8a;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 0.5rem;
    margin-top: 1.8rem;
    animation: fade-in 0.6s ease-out 0.5s forwards;
    opacity: 0;
}

.signin-btn:hover:not(:disabled) {
    background: #1e40af;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(30, 58, 138, 0.25);
}

.signin-btn:active:not(:disabled) {
    transform: translateY(1px);
    box-shadow: none;
}

.signin-btn:focus-visible {
    outline: 3px solid #60a5fa;
    outline-offset: 2px;
}

.signin-btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
}

.offline-divider {
    text-align: center;
    position: relative;
    margin: 1.5rem 0 1rem;
    animation: fade-in 0.6s ease-out 0.6s forwards;
    opacity: 0;
}

.offline-divider span {
    background: transparent;
    color: #94a3b8;
    font-size: 0.75rem;
    font-weight: 600;
}

.offline-btn {
    width: 100%;
    padding: 0.75rem;
    background: transparent;
    color: #475569;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    font-size: 0.95rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    animation: fade-in 0.6s ease-out 0.7s forwards;
    opacity: 0;
    gap: 4px;
}

.offline-btn:hover:not(:disabled) {
    background: #f1f5f9;
    border-color: #94a3b8;
}

.offline-subtitle {
    font-size: 0.75rem;
    font-weight: 400;
    color: #64748b;
}

.security-text {
    text-align: center;
    font-size: 0.75rem;
    color: #64748b;
    margin-top: 1.8rem;
    animation: fade-in 0.6s ease-out 0.8s forwards;
    opacity: 0;
    line-height: 1.4;
}

.login-error {
    background: #fef2f2;
    border: 1px solid #fecaca;
    color: #ef4444;
    padding: 0.85rem;
    border-radius: 8px;
    font-size: 0.9rem;
    margin-bottom: 1.2rem;
    text-align: center;
    animation: slide-down 0.3s ease-out forwards;
}

.login-footer {
    position: relative;
    z-index: 2;
    background: #1e293b;
    color: #94a3b8;
    padding: 1.2rem 3rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.8rem;
    animation: fade-in 1s ease-out forwards;
}

.footer-links {
    display: flex;
    gap: 1.5rem;
}

.footer-links a {
    color: #cbd5e1;
    text-decoration: none;
    transition: color 0.2s;
}

.footer-links a:hover {
    color: #ffffff;
}

.footer-links .separator {
    color: #475569;
}

.footer-credits {
    text-align: right;
    line-height: 1.5;
}

/* Animations */
@keyframes fade-up {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes fade-in {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes fade-in-left {
    from { opacity: 0; transform: translateX(-20px); }
    to { opacity: 1; transform: translateX(0); }
}

@keyframes slide-down {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Responsive */
@media (max-width: 1024px) {
    .promo-headline {
        font-size: 3rem;
    }
}

@media (max-width: 850px) {
    .login-main-content {
        flex-direction: column;
        justify-content: flex-start;
        padding-top: 2rem;
    }
    
    .promo-section {
        padding-left: 0;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .tricolor-line {
        margin: 0 auto 0.5rem;
    }
    
    .login-header {
        flex-direction: column;
        align-items: center;
        gap: 1.5rem;
    }
    
    .login-card-container {
        transform: translateY(0);
    }
}

@media (max-width: 600px) {
    .login-card-container {
        width: 100%;
        max-width: 400px;
    }
    
    .login-card {
        padding: 2rem 1.5rem;
    }
    
    .login-footer {
        flex-direction: column;
        gap: 1rem;
        text-align: center;
    }
    
    .footer-credits {
        text-align: center;
    }
}
"""

with open('src/login.css', 'w', encoding='utf-8') as f:
    f.write(css_content)

print("Wrote login.css")
