import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { logout as apiLogout } from "@/lib/api";

/**
 * Next.js API Route: POST /api/auth/logout
 * 
 * Calls the backend to blacklist the token and then clears the local cookie.
 */
export async function POST() {
  const cookieStore = cookies();
  const token = cookieStore.get("access_token")?.value;

  if (token) {
    try {
      // Notify backend to blacklist the token
      await apiLogout(token);
    } catch (error) {
      // Log error but continue with cookie clearing
      console.error("Backend logout failed:", error);
    }
  }

  // Clear the cookie regardless of backend status
  cookieStore.delete("access_token");

  return NextResponse.json({ message: "Logout successful" });
}
