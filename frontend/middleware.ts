import { NextRequest, NextResponse } from 'next/server';

export function middleware(request: NextRequest) {
  const forwardedHeaders = new Headers(request.headers);
  forwardedHeaders.set('x-forma-client-ip', request.ip ?? 'unknown');
  return NextResponse.next({ request: { headers: forwardedHeaders } });
}

export const config = { matcher: ['/api/v1/:path*'] };
