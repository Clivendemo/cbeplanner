import { ScrollViewStyleReset } from 'expo-router/html';
import { type PropsWithChildren } from 'react';

/**
 * Root HTML document for Expo Web static output.
 * Used to inject global `<head>` content (AdSense, meta tags, etc.)
 * that applies to every exported page.
 */
export default function Root({ children }: PropsWithChildren) {
  return (
    <html lang="en-KE">
      <head>
        <title>CBE Planner - Lesson Plans & Schemes of Work for Kenyan CBC Teachers</title>
        <meta
            name="description"
            content="CBE Planner helps Kenyan CBC teachers instantly generate lesson plans, schemes of work, and lesson notes aligned to KICD guidelines — for all grades and subjects."
        />
        <meta charSet="utf-8" />
        <meta httpEquiv="X-UA-Compatible" content="IE=edge" />
        <meta
          name="viewport"
          content="width=device-width, initial-scale=1, shrink-to-fit=no"
        />
        <meta property="og:type" content="website" />
        <meta property="og:url" content="https://cbeplanner.com/" />
        <meta property="og:title" content="CBE Planner – Lesson Plans & Schemes of Work for Kenyan CBC Teachers" />
        <meta property="og:description" content="Instantly generate CBC-aligned lesson plans, schemes of work, and lesson notes. Built for Kenyan teachers, covering all grades and subjects." />
        <meta property="og:image" content="https://cbeplanner.com/assets/images/app-image.png" />
        <meta property="og:site_name" content="CBE Planner" />
        <meta property="og:locale" content="en_KE" />

        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="CBE Planner – Lesson Plans & Schemes of Work for Kenyan CBC Teachers" />
        <meta name="twitter:description" content="Instantly generate CBC-aligned lesson plans, schemes of work, and lesson notes for Kenyan teachers." />
        <meta name="twitter:image" content="https://cbeplanner.com/assets/images/app-image.png" />

        <meta name="canonical" content="https://cbeplanner.com/" />

        <link rel="icon" type="image/png" sizes="32x32" href="/assets/images/favicon.png" />
        <link rel="icon" type="image/png" sizes="16x16" href="/assets/images/favicon.png" />
        <link rel="apple-touch-icon" sizes="180x180" href="/assets/images/icon.png" />
        <link rel="manifest" href="/manifest.json" />
        <meta name="theme-color" content="#6366F1" />

        {/* Google AdSense */}
        <script
          async
          src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5294485814743596"
          crossOrigin="anonymous"
        />

        {/* ✅ ADD GOOGLE ANALYTICS RIGHT HERE */}
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-74L90635K6"></script>
        <script
          dangerouslySetInnerHTML={{
          __html: `
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
          gtag('config', 'G-74L90635K6');
          `,
        }}
        />

        {/* Premium display font for the news marquee */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,600;1,700&display=swap"
          rel="stylesheet"
        />

        <ScrollViewStyleReset />

        {/* Ensure the app fills the full browser viewport */}
        <style
          // eslint-disable-next-line react/no-danger
          dangerouslySetInnerHTML={{
            __html: `
              html, body, #root {
                height: 100%;
                margin: 0;
                padding: 0;
                min-height: 100vh;
              }
              body {
                overflow-x: hidden;
                /* World-class premium background: a layered purple/lavender wash
                   with a large ambient glow and a slow-moving gleam that sweeps
                   across the viewport. Richer than a flat gradient, but still
                   restrained so content stays the hero. */
                background-color: #EFEAFC;
                background-image:
                  /* Soft lavender glow, top-left */
                  radial-gradient(1200px 820px at 8% 0%, #DDD3FB 0%, transparent 55%),
                  /* Cool indigo glow, top-right */
                  radial-gradient(1000px 700px at 100% 12%, #E7DFFD 0%, transparent 60%),
                  /* Warm magenta-purple haze, bottom-right */
                  radial-gradient(1100px 760px at 92% 100%, #EADDFC 0%, transparent 55%),
                  /* Base diagonal gradient */
                  linear-gradient(135deg, #F5F1FF 0%, #FBF8FF 50%, #EFE7FE 100%);
                background-attachment: fixed;
              }
              /* ===== Premium shimmer layer behind everything ===== */
              body::before {
                content: '';
                position: fixed;
                top: 0; left: 0; right: 0; bottom: 0;
                pointer-events: none;
                z-index: 0;
                background:
                  /* Soft drifting lavender orb */
                  radial-gradient(780px 460px at 18% 28%,
                    rgba(167, 139, 250, 0.22) 0%,
                    rgba(167, 139, 250, 0.00) 65%),
                  /* Cool amethyst counter-orb on the opposite side */
                  radial-gradient(640px 420px at 82% 78%,
                    rgba(139, 92, 246, 0.16) 0%,
                    rgba(139, 92, 246, 0.00) 70%);
                animation: cbepl-glow-drift 28s ease-in-out infinite alternate;
                filter: blur(2px);
              }
              /* ===== Diagonal gleam streak — subtle, ~24s cycle ===== */
              body::after {
                content: '';
                position: fixed;
                top: -20%; left: -40%; right: -40%; bottom: -20%;
                pointer-events: none;
                z-index: 0;
                background: linear-gradient(
                  110deg,
                  rgba(255,255,255,0) 42%,
                  rgba(255,255,255,0.55) 50%,
                  rgba(221, 214, 254, 0.35) 54%,
                  rgba(255,255,255,0) 62%
                );
                transform: translateX(-60%) rotate(4deg);
                animation: cbepl-gleam-sweep 24s ease-in-out infinite;
                mix-blend-mode: screen;
                opacity: 0.55;
              }
              @keyframes cbepl-glow-drift {
                0%   { transform: translate3d(-3%, -2%, 0) scale(1.00); opacity: 0.90; }
                50%  { transform: translate3d(4%,  3%, 0) scale(1.06); opacity: 1.00; }
                100% { transform: translate3d(-2%, 4%, 0) scale(1.02); opacity: 0.92; }
              }
              @keyframes cbepl-gleam-sweep {
                0%   { transform: translateX(-60%) rotate(4deg); }
                55%  { transform: translateX(-60%) rotate(4deg); }
                100% { transform: translateX(60%)  rotate(4deg); }
              }
              @media (prefers-reduced-motion: reduce) {
                body::before, body::after { animation: none !important; }
              }
              /* Keep the actual app tree above the glow layer */
              #root { position: relative; z-index: 1; }

              /* ===== News strip marquee ===== */
              .cbepl-news-strip {
                position: relative;
                overflow: hidden;
                padding: 10px 0;
                background:
                  linear-gradient(90deg, #2E1065 0%, #5B21B6 35%, #7C3AED 70%, #A78BFA 100%);
                border-bottom: 1px solid rgba(255,255,255,0.08);
                box-shadow:
                  inset 0 1px 0 rgba(255,255,255,0.15),
                  inset 0 -1px 0 rgba(0,0,0,0.25),
                  0 2px 6px rgba(76, 29, 149, 0.35);
              }
              .cbepl-news-strip::after {
                /* "Lazy gleam": soft diagonal streak sweeping across the strip. */
                content: '';
                position: absolute;
                inset: 0;
                background: linear-gradient(
                  110deg,
                  rgba(255,255,255,0) 20%,
                  rgba(255,255,255,0.28) 50%,
                  rgba(255,255,255,0) 80%
                );
                transform: translateX(-100%);
                animation: cbepl-gleam 14s ease-in-out infinite;
                pointer-events: none;
              }
              @keyframes cbepl-gleam {
                0%   { transform: translateX(-100%); }
                60%  { transform: translateX(-100%); }
                100% { transform: translateX(140%); }
              }
              .cbepl-news-track {
                display: inline-flex;
                white-space: nowrap;
                padding-left: 100%;
                /* Slowed down (~20% slower) so users can comfortably read */
                animation: cbepl-scroll var(--scroll-duration, 70s) linear infinite;
              }
              .cbepl-news-strip:hover .cbepl-news-track {
                animation-play-state: paused;
              }
              @keyframes cbepl-scroll {
                from { transform: translateX(0); }
                to   { transform: translateX(-100%); }
              }
              .cbepl-news-item {
                display: inline-flex;
                align-items: center;
                gap: 12px;
                padding: 0 36px;
                /* Beautiful serif-display font for the ticker — premium feel */
                font-family: 'Playfair Display', 'Cormorant Garamond', 'Merriweather', Georgia, serif;
                font-size: 17px;
                font-weight: 600;
                color: #F5EFFF;
                letter-spacing: 0.3px;
                /* 3D raised effect via stacked text shadows */
                text-shadow:
                  0 1px 0 rgba(255,255,255,0.18),
                  0 2px 0 rgba(76, 29, 149, 0.55),
                  0 3px 0 rgba(46, 16, 101, 0.55),
                  0 4px 10px rgba(0, 0, 0, 0.45),
                  0 0 18px rgba(167, 139, 250, 0.5);
              }
              .cbepl-news-item strong {
                color: #FFFFFF;
                font-weight: 700;
                font-style: italic;
                margin-right: 6px;
                text-shadow:
                  0 1px 0 rgba(255,255,255,0.25),
                  0 2px 0 rgba(76, 29, 149, 0.6),
                  0 3px 0 rgba(46, 16, 101, 0.6),
                  0 4px 10px rgba(0, 0, 0, 0.5);
              }
              .cbepl-news-bullet {
                width: 7px; height: 7px; border-radius: 50%;
                background: rgba(255,255,255,0.85);
                display: inline-block;
                box-shadow:
                  0 0 8px rgba(255,255,255,0.8),
                  0 0 16px rgba(167, 139, 250, 0.7);
              }
              @media (max-width: 640px) {
                .cbepl-news-strip { padding: 8px 0; }
                .cbepl-news-item { font-size: 15px; padding: 0 24px; gap: 10px; }
                .cbepl-news-track { animation-duration: 50s; }
              }

              /* ===== Global footer ===== */
              .cbepl-footer {
                text-align: center;
                padding: 18px 16px;
                font-size: 12px;
                color: #6B7280;
                background: rgba(255, 255, 255, 0.6);
                border-top: 1px solid rgba(229, 231, 235, 0.8);
                backdrop-filter: blur(6px);
              }
              .cbepl-footer a { color: #6D28D9; text-decoration: none; }
              .cbepl-footer a:hover { text-decoration: underline; }
            `,
          }}
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
