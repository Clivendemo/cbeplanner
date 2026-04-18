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
                background-color: #F3F4F6;
              }
              body { overflow-x: hidden; }
            `,
          }}
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
