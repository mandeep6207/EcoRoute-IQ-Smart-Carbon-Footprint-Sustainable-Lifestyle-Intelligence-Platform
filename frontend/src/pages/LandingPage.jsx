import React from 'react'
import { Link } from 'react-router-dom'

const features = [
  {
    title: 'Carbon footprint intelligence',
    text: 'Analyze travel, electricity, diet, and recycling behavior in one clean monthly view.',
  },
  {
    title: 'Actionable recommendations',
    text: 'Get prioritized sustainability actions based on your highest impact sources.',
  },
  {
    title: 'Progress over time',
    text: 'Track your footprint history, compare changes, and keep your score moving down.',
  },
]

export default function LandingPage() {
  return (
    <div className="landing-page">
      <div className="hero-shell">
        <div className="hero-copy landing-reveal landing-reveal-1">
          <span className="hero-kicker">EcoRoute IQ</span>
          <h1>Turn everyday habits into measurable climate intelligence.</h1>
          <p>
            EcoRoute IQ helps users understand their carbon footprint, identify the biggest emission sources,
            and follow personalized reduction opportunities through a polished SaaS experience.
          </p>
          <div className="hero-actions">
            <Link to="/signup" className="btn btn-primary btn-lg">Create account</Link>
            <Link to="/login" className="btn btn-outline-light btn-lg">Sign in</Link>
          </div>
          <div className="hero-metrics">
            <div>
              <strong>0-100</strong>
              <span>carbon score</span>
            </div>
            <div>
              <strong>Monthly</strong>
              <span>CO₂ insights</span>
            </div>
            <div>
              <strong>Actionable</strong>
              <span>recommendations</span>
            </div>
          </div>
        </div>

        <div className="hero-panel landing-reveal landing-reveal-2">
          <div className="floating-card floating-card-top float-delay-1">
            <div className="label">Latest score</div>
            <div className="value">38 / 100</div>
            <div className="subtext">Moderate Impact</div>
          </div>
          <div className="floating-card floating-card-mid float-delay-2">
            <div className="label">Top source</div>
            <div className="value">Transport</div>
            <div className="subtext">High leverage opportunity</div>
          </div>
          <div className="floating-card floating-card-bottom float-delay-3">
            <div className="label">Monthly CO₂</div>
            <div className="value">186 kg</div>
            <div className="subtext">Based on lifestyle profile</div>
          </div>
        </div>
      </div>

      <section className="feature-grid">
        {features.map((feature, index) => (
          <article key={feature.title} className={`feature-card landing-reveal landing-reveal-${index + 1}`}>
            <h3>{feature.title}</h3>
            <p>{feature.text}</p>
          </article>
        ))}
      </section>

      <section className="cta-band">
        <div>
          <p className="eyebrow">Next step</p>
          <h2>Capture your lifestyle data and see your footprint in seconds.</h2>
        </div>
        <Link to="/signup" className="btn btn-light btn-lg">Start free</Link>
      </section>
    </div>
  )
}
