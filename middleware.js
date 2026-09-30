export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - icons (we need the logo to load on the login screen!)
     * - manifest.json
     */
    '/((?!_next/static|_next/image|favicon.ico|icons/|manifest.json).*)',
  ],
};

const TARGET_HASH = '3c4f148415ce365dba3e90b5bee5335930eeb803814de7424b8218ef18004d6d';

// Function to generate the shadcn-style login HTML
function getLoginHTML(isError = false) {
  return `
<!DOCTYPE html>
<html lang="fr" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Shielder Hub — Accès Sécurisé</title>
    <link rel="icon" type="image/svg+xml" href="/icons/icon.svg">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <script>
      tailwind.config = {
        darkMode: 'class',
        theme: {
          extend: {
            colors: {
              background: '#09090b',
              foreground: '#fafafa',
              card: '#09090b',
              border: 'rgba(255,255,255,0.1)',
              primary: '#2563eb',
              'primary-foreground': '#ffffff',
              muted: 'rgba(255,255,255,0.05)',
              destructive: '#ef4444'
            }
          }
        }
      }
    </script>
</head>
<body class="bg-background text-foreground min-h-screen flex items-center justify-center p-4 antialiased">
    
    <div class="max-w-[400px] w-full rounded-xl border border-border bg-card p-6 sm:p-8 shadow-2xl flex flex-col items-center">
        <!-- Logo -->
        <div class="mb-6 w-16 h-16 rounded-2xl shadow-lg shadow-emerald-500/20 shrink-0">
            <img src="/icons/icon.svg" alt="Shielder Logo" class="w-full h-full object-cover rounded-2xl">
        </div>
        
        <div class="text-center mb-8 w-full">
            <h1 class="text-xl font-bold tracking-tight mb-1.5">Accès Sécurisé</h1>
            <p class="text-sm text-gray-400">Veuillez saisir votre code d'accès pour déverrouiller le Hub.</p>
        </div>

        <form method="POST" action="/login" class="w-full space-y-4">
            <div class="space-y-2">
                <div class="relative">
                    <i data-lucide="lock" class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400"></i>
                    <input type="password" name="code" placeholder="Code d'accès" required autofocus
                        class="w-full bg-muted border border-border rounded-lg pl-10 pr-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all placeholder:text-gray-500">
                </div>
                ${isError ? '<p class="text-xs text-destructive font-medium flex items-center gap-1"><i data-lucide="alert-circle" class="w-3 h-3"></i> Code incorrect, veuillez réessayer.</p>' : ''}
            </div>
            
            <button type="submit" class="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-semibold text-sm py-2.5 rounded-lg shadow-md transition-all flex items-center justify-center gap-2">
                Déverrouiller <i data-lucide="arrow-right" class="w-4 h-4"></i>
            </button>
        </form>
    </div>

    <script>
      lucide.createIcons();
    </script>
</body>
</html>
  `;
}

export default async function middleware(request) {
  const url = new URL(request.url);

  // 1. Handle POST /login (Form submission)
  if (url.pathname === '/login' && request.method === 'POST') {
    try {
      const formData = await request.formData();
      const code = formData.get('code');

      if (code) {
        // Hash the code
        const encoder = new TextEncoder();
        const data = encoder.encode(code);
        const hashBuffer = await crypto.subtle.digest('SHA-256', data);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');

        if (hashHex === TARGET_HASH) {
          // Success! Set HTTPOnly cookie and redirect to dashboard
          return new Response(null, {
            status: 302,
            headers: {
              'Location': '/',
              'Set-Cookie': `shielder_auth_hash=${hashHex}; Path=/; HttpOnly; SameSite=Lax; Max-Age=31536000`
            }
          });
        }
      }
    } catch (e) {
      // Ignore errors and fall through to redirect
    }

    // Failure: Redirect back to login with error
    return new Response(null, {
      status: 302,
      headers: {
        'Location': '/?error=1'
      }
    });
  }

  // 2. Protect all other routes
  const cookieHeader = request.headers.get('cookie') || '';
  const isAuthenticated = cookieHeader.includes(`shielder_auth_hash=${TARGET_HASH}`);

  if (isAuthenticated) {
    // Let the request pass through to the static HTML files
    return;
  }

  // Not authenticated: Serve the beautiful custom login page
  const isError = url.searchParams.get('error') === '1';
  return new Response(getLoginHTML(isError), {
    status: 401, // Unauthorized, but returning HTML
    headers: {
      'Content-Type': 'text/html; charset=utf-8',
    }
  });
}
