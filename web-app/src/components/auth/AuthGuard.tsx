"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { decodeToken, getTokenFromCookie, isTokenExpired, hasRequiredRole } from "@/lib/auth";
import type { TokenPayload } from "@/types";

interface AuthGuardProps {
  children: React.ReactNode;
}

/**
 * Client-side Authentication Guard.
 * 
 * This component performs client-side validation of the JWT:
 * 1. Checks if the token exists in cookies.
 * 2. Checks if the token is expired.
 * 3. Checks if the user has the required role for the current path.
 * 
 * Note: Server-side protection is also handled by middleware.ts. 
 * This Guard provides extra responsiveness and handles token expiration 
 * during long-running client sessions.
 */
export default function AuthGuard({ children }: AuthGuardProps) {
  const router = useRouter();
  const pathname = usePathname();
  const [authorized, setAuthorized] = useState(false);

  useEffect(() => {
    function checkAuth() {
      // Public paths don't need guard (e.g., /login, /forgot-password)
      const isPublicPath = ["/login", "/forgot-password", "/reset-password", "/403"].some(
        (path) => pathname.startsWith(path)
      );
      
      if (isPublicPath) {
        setAuthorized(true);
        return;
      }

      const token = getTokenFromCookie();
      
      if (!token) {
        setAuthorized(false);
        router.push("/login");
        return;
      }

      const payload = decodeToken(token);
      
      if (!payload || isTokenExpired(payload)) {
        setAuthorized(false);
        router.push("/login");
        return;
      }

      if (!hasRequiredRole(payload.role, pathname)) {
        setAuthorized(false);
        router.push("/403");
        return;
      }

      setAuthorized(true);
    }

    checkAuth();
  }, [pathname, router]);

  // Optionally show a loading state while checking auth
  if (!authorized) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return <>{children}</>;
}
