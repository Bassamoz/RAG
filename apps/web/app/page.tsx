import { checkService } from "@store/api-client";
import { apiOrigin } from "../src/config";

export const dynamic = "force-dynamic";

export default async function Home() {
  // A failed network probe is an unavailable state; invalid startup config still throws.
  const ready = await checkService(apiOrigin()).catch(() => false);
  return (
    <main>
      <span className="brand">مستشار المتجر</span>
      <h1>إجابات تبدأ من معرفة متجرك.</h1>
      <p>نعمل على تجهيز الخدمة.</p>
      <p role="status" className="status">
        {ready
          ? "الاتصال متاح. يجري تجهيز بقية الخدمة."
          : "الخدمة غير جاهزة حاليًا. يرجى المحاولة لاحقًا."}
      </p>
    </main>
  );
}
