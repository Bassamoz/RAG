import "server-only";

export function apiOrigin(): string {
  const raw = process.env.API_ORIGIN;
  try {
    const url = new URL(raw ?? "");
    if (
      !["http:", "https:"].includes(url.protocol) ||
      url.username ||
      url.password
    )
      throw new Error();
    if (url.pathname !== "/" || url.search || url.hash) throw new Error();
    return url.origin;
  } catch {
    throw new Error("Invalid or missing configuration: API_ORIGIN");
  }
}
