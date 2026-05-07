class AiCoachSection extends HTMLElement {
    connectedCallback() {
        this.innerHTML = `
            <section class="ai-coach-section" id="coach">
                <div class="container coach-grid">

                    <!-- LEFT TEXT -->
                    <div class="coach-content animate-on-scroll">
                        <div class="section-tag">
                            <svg viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
                            AI Chat Coach
                        </div>
                        <h2>Your personal AI<br>study coach</h2>
                        <p>Ask anything about your performance. The AI coach knows your exact data and gives hyper-personalized answers—not generic tips.</p>

                        <ul class="coach-features">
                            <li>
                                <span class="cf-icon">
                                    <svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>
                                </span>
                                Identifies exactly where you're losing marks
                            </li>
                            <li>
                                <span class="cf-icon">
                                    <svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>
                                </span>
                                Suggests resources based on weak topics
                            </li>
                            <li>
                                <span class="cf-icon">
                                    <svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>
                                </span>
                                Tracks your improvement over time
                            </li>
                            <li>
                                <span class="cf-icon">
                                    <svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>
                                </span>
                                Builds personalised 2-week study plans
                            </li>
                        </ul>
                    </div>

                    <!-- RIGHT CHAT MOCKUP -->
                    <div class="coach-mockup animate-on-scroll" style="transition-delay:200ms">
                        <div class="chat-mockup">

                            <!-- Header -->
                            <div class="chat-header">
                                <div class="chat-header-icon">
                                    <svg viewBox="0 0 24 24"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
                                </div>
                                <div class="chat-header-text">
                                    <h4>IntelliMind Coach</h4>
                                    <p>Your data loaded · Online</p>
                                </div>
                                <div class="chat-header-status">
                                    <div class="status-pulse"></div>
                                    Online
                                </div>
                            </div>

                            <!-- Messages -->
                            <div class="chat-body">
                                <div class="msg-row msg-bot">
                                    <div class="avatar avatar-im">IM</div>
                                    <div class="msg-bubble">
                                        Hi Arjun! 👋 I've analysed your latest performance. You're doing great in OWL Coding (<strong>82%</strong>), but your Verbal APT is at <strong>54%</strong>—want a focused plan?
                                    </div>
                                </div>

                                <div class="msg-row msg-user">
                                    <div class="avatar avatar-user">AK</div>
                                    <div class="msg-bubble">Yes! What topics should I focus on first?</div>
                                </div>

                                <div class="msg-row msg-bot">
                                    <div class="avatar avatar-im">IM</div>
                                    <div class="msg-bubble">
                                        Based on your data, prioritise:<br>
                                        <strong>1) Synonyms &amp; Antonyms</strong> (38% accuracy)<br>
                                        <strong>2) Reading Comprehension</strong> (45%)<br>
                                        <strong>3) Para Jumbles</strong> (52%)<br><br>
                                        I'll build a 2-week plan—shall I?
                                    </div>
                                </div>

                                <div class="msg-row msg-bot">
                                    <div class="avatar avatar-im">IM</div>
                                    <div class="typing-indicator">
                                        <span></span><span></span><span></span>
                                    </div>
                                </div>
                            </div>

                            <!-- Input -->
                            <div class="chat-input-area">
                                <div class="chat-input-box">Ask about your performance…</div>
                                <button class="chat-send-btn" onclick="window.location.href='chat/index.html'">
                                    <svg viewBox="0 0 24 24"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
                                </button>
                            </div>

                        </div>
                    </div>

                </div>
            </section>
        `;
    }
}
customElements.define('ai-coach-section', AiCoachSection);
