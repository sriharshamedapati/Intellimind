class UnifiedPlatforms extends HTMLElement {
    connectedCallback() {
        this.innerHTML = `
            <section class="unified-platforms" id="platforms">
                <div class="container platforms-grid">

                    <!-- LEFT -->
                    <div class="platforms-content animate-on-scroll">
                        <div class="section-tag">
                            <svg viewBox="0 0 24 24"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
                            Platforms
                        </div>
                        <h2>Two platforms.<br>One unified<br>intelligence.</h2>
                        <p>IntelliMind seamlessly connects Maya and HOOT to give you a complete picture of your learning journey across all modules.</p>

                        <div class="platform-tabs">
                            <button class="platform-tab active" id="tabMaya">
                                <svg viewBox="0 0 24 24"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="m8 21 4-4 4 4"/></svg>
                                Maya Platform
                            </button>
                            <button class="platform-tab" id="tabHoot">
                                <svg viewBox="0 0 24 24"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/></svg>
                                HOOT App
                            </button>
                        </div>
                    </div>

                    <!-- RIGHT VISUAL -->
                    <div class="platforms-visual animate-on-scroll" style="transition-delay:200ms">
                        <div class="platform-stat-chip">
                            <div class="psc-icon" style="background:#edfce7">
                                <svg viewBox="0 0 24 24" stroke="var(--green)"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>
                            </div>
                            <div class="psc-val">
                                <span>Overall Score</span>
                                <strong>78% ↑</strong>
                            </div>
                        </div>

                        <div class="modules-card">
                            <div class="modules-card-head">
                                <span class="mch-title" id="modulesCardTitle">Maya Platform</span>
                                <span class="mch-badge">Live Data</span>
                            </div>
                            <div class="modules-list" id="modulesList"></div>
                        </div>
                    </div>

                </div>
            </section>
        `;

        /* ── DATA ── */
        const platforms = {
            maya: {
                label: 'Maya Platform',
                modules: [
                    { dot: 'dot-green',  name: 'OWL Coding Practice',   badge: '150+ topics' },
                    { dot: 'dot-yellow', name: 'APT – Aptitude Logic',   badge: '85 topics'  },
                    { dot: 'dot-green-light', name: 'Technical Core',         badge: '120 topics' },
                    { dot: 'dot-pink',   name: 'Interview Prep',         badge: '45 topics'  },
                ]
            },
            hoot: {
                label: 'HOOT App',
                modules: [
                    { dot: 'dot-green',  name: 'Listening Skills',       badge: '18 topics' },
                    { dot: 'dot-yellow', name: 'Speaking Practice',      badge: '22 topics' },
                    { dot: 'dot-green-light', name: 'Reading Comprehension',  badge: '16 topics' },
                    { dot: 'dot-pink',   name: 'Writing Skills',         badge: '20 topics' },
                ]
            }
        };

        const tabMaya  = this.querySelector('#tabMaya');
        const tabHoot  = this.querySelector('#tabHoot');
        const listEl   = this.querySelector('#modulesList');
        const titleEl  = this.querySelector('#modulesCardTitle');

        const renderModules = (key) => {
            const data = platforms[key];
            titleEl.textContent = data.label;
            listEl.innerHTML = data.modules.map(m => `
                <div class="module-item">
                    <div class="module-info">
                        <div class="module-dot ${m.dot}"></div>
                        ${m.name}
                    </div>
                    <div class="module-badge">${m.badge}</div>
                </div>
            `).join('');
        };

        const switchTab = (key) => {
            listEl.classList.add('fade-out');
            setTimeout(() => {
                renderModules(key);
                listEl.classList.remove('fade-out');
            }, 280);
        };

        // Init
        renderModules('maya');

        tabMaya.addEventListener('click', () => {
            if (tabMaya.classList.contains('active')) return;
            tabMaya.classList.add('active');
            tabHoot.classList.remove('active');
            switchTab('maya');
        });

        tabHoot.addEventListener('click', () => {
            if (tabHoot.classList.contains('active')) return;
            tabHoot.classList.add('active');
            tabMaya.classList.remove('active');
            switchTab('hoot');
        });
    }
}
customElements.define('unified-platforms', UnifiedPlatforms);
