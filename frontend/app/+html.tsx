import { ScrollViewStyleReset } from 'expo-router/html';
import { type PropsWithChildren } from 'react';

/**
 * Root HTML document for Expo Web static output.
 * Used to inject global `<head>` content (AdSense, meta tags, etc.)
 * that applies to every exported page.
 */
export default function Root({ children }: PropsWithChildren) {
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta httpEquiv="X-UA-Compatible" content="IE=edge" />
        <meta
          name="viewport"
          content="width=device-width, initial-scale=1, shrink-to-fit=no"
        />

        {/* Google AdSense */}
        <script
          async
          src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5294485814743596"
          crossOrigin="anonymous"
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
                /* World-class premium background: soft purple → white → lavender
                   with a faint radial glow that shifts slowly for the "gleam" feel. */
                background-color: #F6F4FE;
                background-image:
                  radial-gradient(1200px 800px at 10% 5%, #EDE9FE 0%, transparent 55%),
                  radial-gradient(1200px 800px at 90% 95%, #F5F3FF 0%, transparent 55%),
                  linear-gradient(135deg, #F8F7FF 0%, #FFFFFF 45%, #F3EFFE 100%);
                background-attachment: fixed;
              }
              /* Slow, premium shimmer glow layered behind all content */
              body::before {
                content: '';
                position: fixed;
                top: 0; left: 0; right: 0; bottom: 0;
                pointer-events: none;
                z-index: 0;
                background:
                  radial-gradient(700px 400px at var(--glow-x, 20%) var(--glow-y, 30%),
                    rgba(167, 139, 250, 0.18) 0%,
                    rgba(167, 139, 250, 0.00) 60%);
                animation: cbepl-glow-drift 22s ease-in-out infinite alternate;
              }
              @keyframes cbepl-glow-drift {
                0%   { background-position: 10% 15%; opacity: 0.85; }
                50%  { background-position: 80% 75%; opacity: 1; }
                100% { background-position: 15% 85%; opacity: 0.85; }
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
