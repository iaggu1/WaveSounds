import { NextRequest, NextResponse } from 'next/server';

export function proxy(request: NextRequest) {
  const headers = new Headers(request.headers);

  // Never let a browser choose the address used by the API's rate limiter.
  headers.delete('x-forma-client-ip');

  return NextResponse.next({ request: { headers } });
}

export const config = { matcher: ['/api/v1/:path*'] };

