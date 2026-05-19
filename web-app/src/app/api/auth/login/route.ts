import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { decodeJwt } from "jose";
import { login as apiLogin } from "@/lib/api";

/**
 * Next.js API Route: POST /api/auth/login
 * 
 * This acts as a proxy to the FastAPI backend.
 * On success, it receives a JWT and sets it as an httpOnly cookie.
 */
export async function POST(request: Request) {
  try {
    const { email, password } = await request.json();

    if (!email || !password) {
      return NextResponse.json(
        { detail: "Email and password are required" },
        { status: 400 }
      );
    }

    // Call the actual backend
    const response = await apiLogin(email, password);
    const payload = decodeJwt(response.access_token);
    const role = typeof payload.role === "string" ? payload.role : "student";

    // Set the httpOnly cookie
    const cookieStore = cookies();
    cookieStore.set("access_token", response.access_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      path: "/",
      maxAge: 60 * 60 * 24,
    });

    const redirectTo =
      role === "admin" || role === "super_admin"
        ? "/admin"
        : role === "teacher"
          ? "/teacher"
          : "/dashboard";

    return NextResponse.json({ message: "Login successful", redirectTo });
  } catch (error: any) {
    return NextResponse.json(
      { detail: error.message || "Authentication failed" },
      { status: error.status || 401 }
    );
  }
}
