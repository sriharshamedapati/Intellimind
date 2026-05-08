class HeroSection extends HTMLElement {
    connectedCallback() {
        this.innerHTML = `
            <section class="hero">
                <div class="container hero-grid">

                    <!-- LEFT -->
                    <div class="hero-left animate-on-scroll">

                        <div class="hero-title-block">
                            <span class="line-1">AI LEARNING</span>
                            <div class="line-2-wrapper">
                                <span class="line-2">INTELLIGENCE</span>
                            </div>
                            <span class="line-3">EVOLVED</span>
                        </div>

                        <p class="hero-subtext">
                            Unlock your full potential with a data-driven AI tutoring system. 
                            Receive hyper-personalized insights and adaptive learning paths tailored to your unique academic journey.
                        </p>

                        <div class="hero-buttons">
                            <button class="btn btn-primary" onclick="window.location.href='login/index.html'">
                                Get Started
                                <svg viewBox="0 0 24 24"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
                            </button>
                            <button class="btn btn-outline" onclick="document.getElementById('features').scrollIntoView({behavior:'smooth'})">
                                Learn More
                            </button>
                        </div>
                    </div>

                    <!-- RIGHT VISUAL -->
                    <div class="hero-right animate-on-scroll" style="transition-delay:200ms">
                        <div class="hero-effects-container">
                            <div class="abstract-orb-wrapper">
                                <div class="dial-circle"></div>
                                <div class="abstract-orb">
                                    <img src="images/robot.png" alt="IntelliMind AI Robot">
                                </div>
                            </div>

                            <div class="tech-node node-1">
                                <svg viewBox="0 0 24 24"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
                            </div>
                            <div class="tech-node node-2">
                                <svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                            </div>
                            <div class="tech-node node-3">
                                <svg viewBox="0 0 24 24" style="color:var(--yellow)"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
                            </div>

                            <div class="floating-card-1">
                                <div class="fc-left">
                                    <div class="fc-since">Since 2026</div>
                                    <div class="fc-name">
                                        <span class="g">Intelli</span><span class="y">Mind</span>
                                    </div>
                                </div>
                                <div class="fc-divider">
                                    <div class="fc-ai">AI+</div>
                                    <div class="fc-lbl">Insights</div>
                                </div>
                            </div>
                        </div>
                    </div>

                </div>
            </section>
        `;
    }
}
customElements.define('hero-section', HeroSection);
