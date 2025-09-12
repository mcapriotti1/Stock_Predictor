import './globals.css';
import { ReactNode } from 'react';
import Link from 'next/link';

export const metadata = {
  title: 'Stock Forecast',
  description: 'Forecast popular stocks for the next day',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header style={{ padding: '1rem', borderBottom: '1px solid #ccc' }}>
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'flex-start'}}>
            <Link href="/">
              <h1 style={{ cursor: 'pointer', margin: 0, color: 'white' }}>
                Stock Forecast
              </h1>
            </Link>
          </div>
         
        </header>
        <main style={{ padding: '1rem' }}>{children}</main>
        <footer style={{ padding: '1rem', borderTop: '1px solid #ccc', marginTop: '2rem' }}>
          Developed by Michael Capriotti - 
          <a 
            href="https://github.com/" 
            target="_blank" 
            rel="noopener noreferrer"
          >
            Learn More
          </a>
        </footer>
      </body>
    </html>
  );
}
