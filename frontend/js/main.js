/* ============================================================
   main.js
   Stats Banner · Learning Insights · How It Works · CTA · Footer
   + Global Scroll Animation Observer
   ============================================================ */

/* ── STATS BANNER ── */
class StatsBanner extends HTMLElement {
    connectedCallback() {
        this.innerHTML = `
            <section class="stats-banner">
                <div class="stats-grid">
                    <div class="stat-item animate-on-scroll">
                        <div class="stat-icon">
                            <svg viewBox="0 0 24 24"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/><path d="M10 9l3 2-3 2v-4z"/></svg>
                        </div>
                        <div class="stat-info"><h4>100+</h4><p>Courses Available</p></div>
                    </div>
                    <div class="stat-item animate-on-scroll" style="transition-delay:80ms">
                        <div class="stat-icon">
                            <svg viewBox="0 0 24 24"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/></svg>
                        </div>
                        <div class="stat-info"><h4>30,000+</h4><p>Active Trainees</p></div>
                    </div>
                    <div class="stat-item animate-on-scroll" style="transition-delay:160ms">
                        <div class="stat-icon">
                            <svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="6"/><path d="M15.477 12.89 17 22l-5-3-5 3 1.523-9.11"/></svg>
                        </div>
                        <div class="stat-info"><h4>Global</h4><p>Certifications</p></div>
                    </div>
                    <div class="stat-item animate-on-scroll" style="transition-delay:240ms">
                        <div class="stat-icon">
                            <svg viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
                        </div>
                        <div class="stat-info"><h4>Smart</h4><p>Learning Platform</p></div>
                    </div>
                </div>
            </section>
        `;
    }
}
customElements.define('stats-banner', StatsBanner);


/* ── LEARNING INSIGHTS / TOOLS ── */
class LearningInsights extends HTMLElement {
    connectedCallback() {
        const tools = [
            {
                icon: `<svg viewBox="0 0 24 24"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>`,
                title: 'AI Performance Analysis',
                desc:  'Deep analysis of coding, aptitude and communication performance with contextual, actionable insights.'
            },
            {
                icon: `<svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>`,
                title: 'Weak Topic Detection',
                desc:  'Automatically identifies low-performing topics across all modules and flags them for targeted improvement.'
            },
            {
                icon: `<svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>`,
                title: 'AI Learning Planner',
                desc:  'Get personalized daily/weekly study plans based on your performance gaps, deadlines, and learning velocity.'
            },
            {
                icon: `<svg viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>`,
                title: 'AI Chat Coach',
                desc:  'Ask anything about your performance. The AI coach responds with data-driven answers specific to your profile.'
            },
            {
                icon: `<svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/><path d="M9 21V9"/></svg>`,
                title: 'Performance Dashboard',
                desc:  'Visualize your progress across all platforms with real-time charts and Power BI integrated analytics.'
            },
            {
                icon: `<svg viewBox="0 0 24 24"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>`,
                title: 'Interview Prep Mode',
                desc:  'Practice coding, aptitude, and HR interview questions tailored to your detected weak areas.'
            },
        ];

        const cards = tools.map((t, i) => `
            <div class="tool-card animate-on-scroll" style="transition-delay:${i * 60}ms">
                <div class="tool-icon-box">${t.icon}</div>
                <h3>${t.title}</h3>
                <p>${t.desc}</p>
            </div>
        `).join('');

        this.innerHTML = `
            <section class="tools-section" id="features">
                <div class="container">
                    <div class="tools-header">
                        <div class="tools-header-left animate-on-scroll">
                            <div class="section-tag">
                                <svg viewBox="0 0 24 24"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
                                Key Features
                            </div>
                            <h2>Powerful tools for<br>smarter learning</h2>
                            <p>Every insight is backed by AI analysis of your actual performance data—not generic advice.</p>
                        </div>
                    </div>
                    <div class="tools-grid">${cards}</div>
                </div>
            </section>
        `;
    }
}
customElements.define('learning-insights', LearningInsights);


/* ── HOW IT WORKS ── */
class HowItWorksSection extends HTMLElement {
    connectedCallback() {
        const steps = [
            {
                n: '1',
                title: 'Data Collection',
                desc: 'Securely fetches your performance data from Maya and HOOT via institutional APIs and stores it in real-time.'
            },
            {
                n: '2',
                title: 'AI Analysis',
                desc: 'Your data is processed to identify patterns, detect weak topics, and build your personalised performance profile.'
            },
            {
                n: '3',
                title: 'Personalised Growth',
                desc: 'You receive an interactive dashboard, smart study plans, and an AI chat coach—all tailored to your exact learning gaps.'
            },
        ];

        const stepsHtml = steps.map((s, i) => `
            <div class="step animate-on-scroll" style="transition-delay:${i * 130}ms">
                <div class="step-number">${s.n}</div>
                <h3>${s.title}</h3>
                <p>${s.desc}</p>
            </div>
        `).join('');

        this.innerHTML = `
            <section id="about" class="how-it-works">
                <div class="container">
                    <div class="section-header animate-on-scroll">
                        <h2>How <span>IntelliMind</span> Works</h2>
                    </div>
                    <div class="steps-container">${stepsHtml}</div>
                </div>
            </section>
        `;
    }
}
customElements.define('how-it-works-section', HowItWorksSection);


/* ── CTA ── */
class CtaSection extends HTMLElement {
    connectedCallback() {
        this.innerHTML = `
            <section class="cta">
                <div class="container">
                    <div class="cta-content animate-on-scroll">
                        <h2>Ready to transform your learning?</h2>
                        <p>Join thousands of students using IntelliMind's AI insights to master coding, aptitude, and communication skills.</p>
                        <button class="btn-cta" onclick="window.location.href='login/index.html'">
                            Get Started Now
                            <svg viewBox="0 0 24 24"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
                        </button>
                    </div>
                </div>
            </section>
        `;
    }
}
customElements.define('cta-section', CtaSection);


/* ── FOOTER ── */
class AppFooter extends HTMLElement {
    connectedCallback() {
        this.innerHTML = `
            <footer>
                <div class="container">
                    <div class="footer-content">
                        <div class="footer-brand-wrap">
                            <div class="footer-logo">
                                <div class="footer-logo-box">
                                    <svg viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
                                </div>
                                <span>Intelli<span class="y">Mind</span></span>
                            </div>
                            <p>AI Learning Intelligence for Maya &amp; HOOT. Empowering students through data.</p>
                        </div>

                        <div>
                            <div class="footer-col-title">Platform</div>
                            <div class="footer-links">
                                <a href="#features">Features</a>
                                <a href="#platforms">Modules</a>
                                <a href="#about">How It Works</a>
                            </div>
                        </div>

                        <div>
                            <div class="footer-col-title">Account</div>
                            <div class="footer-links">
                                <a href="login/index.html">Login</a>
                                <a href="chat/index.html">Dashboard</a>
                                <a href="chat/index.html">Chat Coach</a>
                            </div>
                        </div>

                        <div>
                            <div class="footer-col-title">Company</div>
                            <div class="footer-links">
                                <a href="#">About</a>
                                <a href="#">Privacy Policy</a>
                                <a href="#">Contact</a>
                            </div>
                        </div>
                    </div>

                    <div class="footer-bottom">
                        &copy; 2026 IntelliMind. All rights reserved. Empowering academic excellence.
                    </div>
                </div>
            </footer>
        `;
    }
}
customElements.define('app-footer', AppFooter);


/* ============================================================
   GLOBAL SCROLL ANIMATION OBSERVER
   Watches for custom elements to finish rendering, then observes
   ============================================================ */
window.addEventListener('load', () => {
    const observer = new IntersectionObserver(
        (entries, obs) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('show');
                    obs.unobserve(entry.target);
                }
            });
        },
        { root: null, rootMargin: '0px', threshold: 0.12 }
    );

    // Delay slightly so all Web Components have rendered
    setTimeout(() => {
        document.querySelectorAll('.animate-on-scroll').forEach(el => observer.observe(el));
    }, 100);
});
