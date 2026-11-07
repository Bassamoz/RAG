export async function register() {
  if (process.env.NEXT_RUNTIME === "nodejs") {
    const { apiOrigin } = await import("./src/config");
    apiOrigin();
  }
}
