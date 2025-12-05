import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
    const { searchParams } = new URL(request.url);
    const url = searchParams.get("url");

    if (!url) {
        return NextResponse.json({ error: "Missing URL param" }, { status: 400 });
    }

    try {
        const imageRes = await fetch(url);
        if (!imageRes.ok) throw new Error("Failed to fetch image");

        // Get Content-Type
        const contentType = imageRes.headers.get("Content-Type") || "image/png";

        // Determine extension
        let ext = "png";
        if (contentType.includes("jpeg")) ext = "jpg";
        else if (contentType.includes("webp")) ext = "webp";

        const headers = new Headers();
        headers.set("Content-Type", contentType);
        headers.set("Content-Disposition", `attachment; filename="panel-one-result.${ext}"`);
        headers.set("Cache-Control", "public, max-age=3600");

        return new NextResponse(imageRes.body, {
            status: 200,
            headers,
        });
    } catch (error) {
        console.error("Proxy error:", error);
        return NextResponse.json({ error: "Failed to fetch image" }, { status: 500 });
    }
}
