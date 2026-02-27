<template>
  <div class="privacy-page">
    <nav class="nav">
      <RouterLink to="/" class="nav__brand">Rentify</RouterLink>
      <div class="nav__links">
        <RouterLink to="/login">Login</RouterLink>
        <RouterLink to="/signup" class="btn-primary">Sign Up</RouterLink>
      </div>
    </nav>

    <main class="content">
      <h1>Privacy Policy</h1>
      <p class="updated">Last updated: 1 January 2024</p>

      <section>
        <h2>1. Data Controller</h2>
        <p>Rentify BV, registered in the Netherlands, is the data controller for all personal data processed through this service.</p>
      </section>

      <section>
        <h2>2. Data We Collect</h2>
        <ul>
          <li><strong>Account data</strong>: email address, full name (optional), password hash</li>
          <li><strong>Search preferences</strong>: city, price range, room count, size, and other rental criteria</li>
          <li><strong>Notification settings</strong>: Telegram chat ID (if connected), email address</li>
          <li><strong>Usage data</strong>: login timestamps, match history</li>
        </ul>
      </section>

      <section>
        <h2>3. Legal Basis (GDPR Article 6)</h2>
        <p>We process your data based on:</p>
        <ul>
          <li><strong>Contract</strong> (Art. 6(1)(b)) — to provide the Rentify service</li>
          <li><strong>Consent</strong> (Art. 6(1)(a)) — for marketing communications (opt-in only)</li>
          <li><strong>Legitimate interest</strong> (Art. 6(1)(f)) — for fraud prevention and service security</li>
        </ul>
      </section>

      <section>
        <h2>4. Cookies</h2>
        <p>We use only technically necessary cookies for authentication (session tokens). We do not use tracking or analytics cookies. No third-party advertising cookies are set.</p>
      </section>

      <section>
        <h2>5. Data Retention</h2>
        <p>Account data is retained for as long as your account is active. Upon deletion, all personal data is permanently removed within 30 days, except where legally required to retain it longer.</p>
      </section>

      <section>
        <h2>6. Your Rights</h2>
        <p>Under GDPR, you have the right to:</p>
        <ul>
          <li><strong>Access</strong> — request a copy of your data</li>
          <li><strong>Rectification</strong> — correct inaccurate data</li>
          <li><strong>Erasure</strong> — request deletion of your account and data</li>
          <li><strong>Portability</strong> — export your data in machine-readable format</li>
          <li><strong>Objection</strong> — object to processing based on legitimate interest</li>
        </ul>
        <p>To exercise these rights, use the account settings page or contact <a href="mailto:privacy@rentify.nl">privacy@rentify.nl</a>.</p>
      </section>

      <section>
        <h2>7. Third-Party Services</h2>
        <p>We use Stripe for payment processing (EU data processing agreement in place) and SendGrid for transactional emails. No data is sold to third parties.</p>
      </section>

      <section>
        <h2>8. Contact</h2>
        <p>For privacy enquiries: <a href="mailto:privacy@rentify.nl">privacy@rentify.nl</a></p>
      </section>
    </main>

    <footer class="footer">
      <p>© 2024 Rentify · EU GDPR Compliant</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<style scoped>
.privacy-page { min-height: 100vh; display: flex; flex-direction: column; }
.nav { display: flex; justify-content: space-between; align-items: center; padding: 1rem 2rem; background: white; border-bottom: 1px solid #e5e7eb; }
.nav__brand { font-size: 1.5rem; font-weight: 700; color: #4f46e5; text-decoration: none; }
.nav__links { display: flex; gap: 1rem; align-items: center; }
.btn-primary { background: #4f46e5; color: white; padding: 0.5rem 1rem; border-radius: 0.5rem; font-weight: 600; text-decoration: none; }
.content { flex: 1; max-width: 800px; margin: 0 auto; padding: 3rem 2rem; }
.content h1 { font-size: 2rem; font-weight: 800; margin-bottom: 0.5rem; }
.updated { color: #6b7280; margin-bottom: 2rem; }
section { margin-bottom: 2rem; }
section h2 { font-size: 1.125rem; font-weight: 700; margin-bottom: 0.75rem; color: #111827; }
section p, section ul { color: #374151; line-height: 1.6; }
section ul { padding-left: 1.5rem; }
section li { margin-bottom: 0.5rem; }
a { color: #4f46e5; }
.footer { padding: 2rem; text-align: center; background: #1a1a2e; color: #9ca3af; }
</style>
