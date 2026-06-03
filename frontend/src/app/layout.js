import './globals.css';

export const metadata = {
  title: 'GigSaathi — AI Tax Assistant for Gig Workers',
  description:
    'GigSaathi is an AI-powered tax assistant built for India\'s booming gig economy. Upload your earnings from Swiggy, Zomato, Uber, Ola, Zerodha & more — and get your ITR-4 filed without a CA.',
  keywords: [
    'gig economy',
    'tax assistant',
    'ITR-4',
    'freelancer tax India',
    'Swiggy',
    'Zomato',
    'Uber',
    'AI tax',
  ],
  icons: {
    icon: '/favicon.ico',
  },
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
