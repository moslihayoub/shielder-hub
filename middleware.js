export const config = {
  matcher: ['/', '/index.html', '/dashboard.html'],
};

export default async function middleware(request) {
  const authHeader = request.headers.get('authorization');

  if (!authHeader) {
    return new Response('Accès sécurisé - Entrez le code', {
      status: 401,
      headers: {
        'WWW-Authenticate': 'Basic realm="Shielder Hub - Sécurisé"',
      },
    });
  }

  try {
    const authValue = authHeader.split(' ')[1];
    const decoded = atob(authValue);
    // basic auth format is "username:password". The user might put "031984" in username or password.
    const parts = decoded.split(':');
    const password = parts[1] || parts[0]; 

    // Hash the entered password via Web Crypto API (SHA-256)
    const encoder = new TextEncoder();
    const data = encoder.encode(password);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');

    // Pre-computed SHA-256 hash of "031984"
    const TARGET_HASH = '3c4f148415ce365dba3e90b5bee5335930eeb803814de7424b8218ef18004d6d';

    if (hashHex === TARGET_HASH) {
      // Authenticated successfully
      return; 
    }
  } catch (e) {
    // decoding error or crypto error
  }

  // Deny access
  return new Response('Code incorrect', {
    status: 401,
    headers: {
      'WWW-Authenticate': 'Basic realm="Shielder Hub - Sécurisé"',
    },
  });
}
