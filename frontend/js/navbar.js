class AppNavbar extends HTMLElement {
    connectedCallback() {
        this.innerHTML = `
            <header class="navbar" id="mainNavbar">
                <div class="container nav-container">
                    <a href="#" class="logo">
                        <div class="logo-icon-wrap">
                            <svg viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" fill="none"><path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"/><path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z"/><path d="M15 13a4.5 4.5 0 0 1-3-4 4.5 4.5 0 0 1-3 4"/><path d="M17.599 6.5a3 3 0 0 0 .399-1.375"/><path d="M6.002 5.125A3 3 0 0 0 6.401 6.5"/><path d="M3.477 10.896a4 4 0 0 1 .585-.396"/><path d="M19.938 10.5a4 4 0 0 1 .585.396"/><path d="M6 18a4 4 0 0 1-1.967-.516"/><path d="M19.967 17.484A4 4 0 0 1 18 18"/></svg>
                        </div>
                        <span><span class="g">INTELL</span><span class="y">MIND</span></span>
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
