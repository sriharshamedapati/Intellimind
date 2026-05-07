class AppNavbar extends HTMLElement {
    connectedCallback() {
        this.innerHTML = `
            <header class="navbar" id="mainNavbar">
                <div class="container nav-container">
                    <a href="#" class="logo">
                        <div class="logo-icon-wrap">
                            <svg viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
                        </div>
                        <span><span class="g">Intelli</span><span class="y">Mind</span></span>
                    </a>
                    <nav class="nav-links">
                        
<a href="login/index.html" class="btn-login">Login</a>                    </nav>
                </div>
            </header>
        `;

        const navbar = this.querySelector('#mainNavbar');
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                navbar.style.boxShadow = '0 4px 24px rgba(0, 0, 0, 0.08)';
            } else {
                navbar.style.boxShadow = '0 2px 10px rgba(0,0,0,0.04)';
            }
        });
    }
}
customElements.define('app-navbar', AppNavbar);
