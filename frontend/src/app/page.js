'use client';

import { useRouter } from 'next/navigation';
import Link from 'next/link';

const personas = [
  {
    id: 'ravi_kumar',
    name: 'Ravi Kumar',
    avatar: '🛵',
    occupation: 'Delivery Partner',
    platforms: ['Swiggy', 'Zomato', 'Dunzo'],
    income: '₹28,000/mo',
    color: '#7c3aed',
  },
  {
    id: 'priya_sharma',
    name: 'Priya Sharma',
    avatar: '💻',
    occupation: 'Freelance Designer',
    platforms: ['Upwork', 'Fiverr', 'Toptal'],
    income: '₹65,000/mo',
    color: '#10b981',
  },
  {
    id: 'arjun_reddy',
    name: 'Arjun Reddy',
    avatar: '🚗',
    occupation: 'Ride-share Driver',
    platforms: ['Uber', 'Ola', 'Rapido'],
    income: '₹35,000/mo',
    color: '#f59e0b',
  },
];

const features = [
  {
    icon: '📄',
    title: 'Upload PDFs',
    description:
      'Drop your earnings statements, bank PDFs, or platform receipts. Our AI extracts everything automatically.',
  },
  {
    icon: '🤖',
    title: 'AI Tax Calculation',
    description:
      'Smart engine computes your taxes under both Old & New regimes. Finds every deduction you deserve.',
  },
  {
    icon: '📋',
    title: 'ITR-4 Ready',
    description:
      'Get a fully filled ITR-4 form ready for filing on the Income Tax portal. Zero CA fees.',
  },
];

export default function LandingPage() {
  const router = useRouter();

  const handlePersonaClick = (personaId) => {
    router.push(`/dashboard?user=${personaId}`);
  };

  return (
    <main className="landing">
      {/* Floating animated background elements */}
      <div className="landing-bg">
        <div className="floating-orb orb-1" />
        <div className="floating-orb orb-2" />
        <div className="floating-orb orb-3" />
        <div className="grid-overlay" />
      </div>

      {/* Navbar */}
      <nav className="landing-nav">
        <div className="nav-brand">
          <span className="nav-logo">⚡</span>
          <span className="nav-title">GigSaathi</span>
        </div>
        <div className="nav-links">
          <Link href="#features" className="nav-link">
            Features
          </Link>
          <Link href="#demo" className="nav-link">
            Demo
          </Link>
          <Link href="/dashboard?user=ravi_kumar" className="btn-primary btn-sm">
            Launch App
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-badge animate-fade-in">
          <span className="badge-dot" />
          Built for India&apos;s 15M+ Gig Workers
        </div>

        <h1 className="hero-title animate-fade-in">
          Your <span className="text-gradient">AI Tax Assistant</span>
          <br />
          for the Gig Economy
        </h1>

        <p className="hero-subtitle animate-fade-in">
          Upload your earnings. Get your taxes done.{' '}
          <strong>No CA needed.</strong>
        </p>

        <div className="hero-actions animate-fade-in">
          <Link href="#demo" className="btn-primary btn-lg">
            Get Started
            <span className="btn-arrow">→</span>
          </Link>
          <Link href="#features" className="btn-ghost btn-lg">
            See How It Works
          </Link>
        </div>

        <div className="hero-stats animate-fade-in">
          <div className="stat-item">
            <span className="stat-value">₹0</span>
            <span className="stat-label">Filing Cost</span>
          </div>
          <div className="stat-divider" />
          <div className="stat-item">
            <span className="stat-value">5 min</span>
            <span className="stat-label">Average Time</span>
          </div>
          <div className="stat-divider" />
          <div className="stat-item">
            <span className="stat-value">99.2%</span>
            <span className="stat-label">Accuracy</span>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section" id="features">
        <h2 className="section-title animate-fade-in">
          Everything you need to <span className="text-gradient">file taxes</span>
        </h2>
        <p className="section-subtitle animate-fade-in">
          From PDF upload to ITR-4 generation — powered by AI, built for simplicity.
        </p>

        <div className="features-grid">
          {features.map((feature, index) => (
            <div
              className="card feature-card animate-fade-in"
              key={index}
              style={{ animationDelay: `${index * 0.15}s` }}
            >
              <div className="feature-icon">{feature.icon}</div>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-desc">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Demo / Persona Selection */}
      <section className="demo-section" id="demo">
        <h2 className="section-title animate-fade-in">
          Try a <span className="text-gradient">live demo</span>
        </h2>
        <p className="section-subtitle animate-fade-in">
          Pick a persona to explore the full dashboard experience.
        </p>

        <div className="personas-grid">
          {personas.map((persona, index) => (
            <button
              key={persona.id}
              className="card persona-card animate-fade-in"
              style={{ animationDelay: `${index * 0.15}s` }}
              onClick={() => handlePersonaClick(persona.id)}
            >
              <div
                className="persona-avatar"
                style={{
                  background: `linear-gradient(135deg, ${persona.color}33, ${persona.color}11)`,
                  borderColor: `${persona.color}55`,
                }}
              >
                <span className="persona-emoji">{persona.avatar}</span>
              </div>
              <h3 className="persona-name">{persona.name}</h3>
              <p className="persona-occupation">{persona.occupation}</p>
              <div className="persona-platforms">
                {persona.platforms.map((platform) => (
                  <span className="platform-tag" key={platform}>
                    {platform}
                  </span>
                ))}
              </div>
              <div className="persona-income">
                <span className="income-label">Avg. Income</span>
                <span className="income-value">{persona.income}</span>
              </div>
              <div
                className="persona-cta"
                style={{ color: persona.color }}
              >
                Explore Dashboard →
              </div>
            </button>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <div className="footer-brand">
          <span className="nav-logo">⚡</span>
          <span>GigSaathi</span>
        </div>
        <p className="footer-text">
          Made with 💜 for India&apos;s gig workers · AI-powered tax filing
        </p>
      </footer>
    </main>
  );
}
