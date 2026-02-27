<template>
  <div class="landing">
    <nav class="nav">
      <div class="nav__brand">Rentify</div>
      <div class="nav__links">
        <RouterLink to="/login">Login</RouterLink>
        <RouterLink to="/signup" class="btn-primary">Start Free Trial</RouterLink>
      </div>
    </nav>

    <section class="hero">
      <div class="hero__content">
        <h1>Find Your Perfect Rental in Europe</h1>
        <p>We search Funda, Pararius, Kamernet and more — so you don't have to. Get instant Telegram alerts when new listings match your criteria.</p>
        <RouterLink to="/signup" class="btn-hero">
          Start your 7-day free trial — then €5/month. Cancel anytime.
        </RouterLink>
      </div>
    </section>

    <section class="features">
      <div class="features__grid">
        <div class="feature">
          <div class="feature__icon">🔍</div>
          <h3>Multi-Site Search</h3>
          <p>Aggregates listings from Funda, Pararius, Kamernet, and more.</p>
        </div>
        <div class="feature">
          <div class="feature__icon">🔔</div>
          <h3>Instant Notifications</h3>
          <p>Telegram and email alerts the moment a match appears.</p>
        </div>
        <div class="feature">
          <div class="feature__icon">🎯</div>
          <h3>Smart Matching</h3>
          <p>Set preferences for city, price, size. We do the rest.</p>
        </div>
        <div class="feature">
          <div class="feature__icon">🔒</div>
          <h3>GDPR Compliant</h3>
          <p>Full data export and deletion. Your data stays yours.</p>
        </div>
      </div>
    </section>

    <footer class="footer">
      <p>© 2024 Rentify · <RouterLink to="/privacy">Privacy Policy</RouterLink> · EU GDPR Compliant</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<style scoped>
.landing { min-height: 100vh; display: flex; flex-direction: column; }
.nav { display: flex; justify-content: space-between; align-items: center; padding: 1rem 2rem; background: white; border-bottom: 1px solid #e5e7eb; }
.nav__brand { font-size: 1.5rem; font-weight: 700; color: #4f46e5; }
.nav__links { display: flex; gap: 1rem; align-items: center; }
.btn-primary { background: #4f46e5; color: white; padding: 0.5rem 1rem; border-radius: 0.5rem; font-weight: 600; text-decoration: none; }
.hero { flex: 1; display: flex; align-items: center; justify-content: center; padding: 4rem 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center; }
.hero__content { max-width: 700px; }
.hero h1 { font-size: clamp(2rem, 5vw, 3rem); font-weight: 800; margin-bottom: 1.5rem; }
.hero p { font-size: 1.2rem; margin-bottom: 2rem; opacity: 0.9; }
.btn-hero { display: inline-block; background: white; color: #4f46e5; padding: 1rem 2rem; border-radius: 0.75rem; font-weight: 700; font-size: 1rem; text-decoration: none; }
.features { padding: 4rem 2rem; background: white; }
.features__grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 2rem; max-width: 900px; margin: 0 auto; }
.feature { text-align: center; padding: 1.5rem; }
.feature__icon { font-size: 2.5rem; margin-bottom: 1rem; }
.footer { padding: 2rem; text-align: center; background: #1a1a2e; color: #9ca3af; }
</style>
