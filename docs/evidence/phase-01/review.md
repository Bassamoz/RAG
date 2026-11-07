# مراجعة مستقلة للمرحلة 01

مراجعة قراءة فقط لوحدات الأساس والـmigrations ومسارات dev/CI والواجهة. المنهج: doubt-driven adversarial review؛ لم يُفوّض المراجع أي كتابة أو نشر.

| الملاحظة المؤكدة | المعالجة | الدليل |
|---|---|---|
| DSN مشوه يمكن أن يكشف جزءًا منه في خطأ parsing عند بدء API | validate_postgres_url مشترك وحارس Redis كامل؛ رسائل حقول آمنة | red-config-url exit1 ثم unit exit0 |
| pnpm.cmd على Windows يُكتشف بالـPATH لكن CreateProcess لا يحل اسمه المختصر | dev.run يستعمل المسار الذي أعاده shutil.which | windows-pnpm-shim exit0 فعليًا |
| Alembic autogenerate كان يعكس مخططات Supabase غير المملوكة | include_name يقتصر على app في configure online/offline | اختبارات منع auth/storage/public/extensions وapp ضمن unit |
| مسار MIGRATION_DATABASE_URL كان يحتفظ بمشكلة parsing نفسها | إعادة استعمال validate_postgres_url، RuntimeError آمن بلا cause | red-migration-url exit1 ثم unit 14 passed |

راجع المراجع إصلاحات الملاحظات الثلاث الأولى. أُصلحت ملاحظة migration DSN بعد تقريره النهائي، واختُبرت محليًا. لا يُعد ذلك تدقيقًا أمنيًا نهائيًا أو تحققًا حيًا لـRLS. عُرض رأي ثانٍ cross-model عبر السؤال المخصص واختار المستخدم «تجاوز الرأي الثاني»؛ لم يُستدع CLI خارجي.
