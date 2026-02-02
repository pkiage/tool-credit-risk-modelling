import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

export function middleware(request: NextRequest) {
	const apiKey = request.cookies.get("api_key");
	const isLoginPage = request.nextUrl.pathname === "/login";

	if (isLoginPage) {
		return NextResponse.next();
	}

	if (!apiKey) {
		return NextResponse.redirect(new URL("/login", request.url));
	}

	return NextResponse.next();
}

export const config = {
	matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
