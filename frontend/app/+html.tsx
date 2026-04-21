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
                background:
                  linear-gradient(90deg, #4C1D95 0%, #6D28D9 50%, #8B5CF6 100%);
              }
              .cbepl-news-strip::after {
                /* "Lazy gleam": soft diagonal streak sweeping across the strip. */
                content: '';
                position: absolute;
                inset: 0;
                background: linear-gradient(
                  110deg,
                  rgba(255,255,255,0) 20%,
                  rgba(255,255,255,0.25) 50%,
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
                animation: cbepl-scroll var(--scroll-duration, 55s) linear infinite;
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
                gap: 10px;
                padding: 0 28px;
                font-size: 13px;
                font-weight: 500;
                color: #F3E8FF;
                letter-spacing: 0.2px;
              }
              .cbepl-news-item strong {
                color: #FFFFFF;
                font-weight: 700;
                margin-right: 6px;
              }
              .cbepl-news-bullet {
                width: 5px; height: 5px; border-radius: 50%;
                background: rgba(255,255,255,0.55);
                display: inline-block;
              }
              @media (max-width: 640px) {
                .cbepl-news-item { font-size: 12px; padding: 0 20px; }
                .cbepl-news-track { animation-duration: 40s; }
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
